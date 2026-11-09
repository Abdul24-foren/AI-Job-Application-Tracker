import csv
import io
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, abort
from .db import get_db
from .analyzer import compare_keywords

bp = Blueprint("main", __name__)
STATUSES = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected", "Withdrawn"]
JOB_TYPES = ["Full-time", "Internship", "Contract", "Part-time", "Remote"]

def clean(value, max_len=2000):
    return (value or "").strip()[:max_len]

def get_application(app_id):
    row = get_db().execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    if row is None:
        abort(404)
    return row

@bp.app_context_processor
def inject_globals():
    return {"statuses": STATUSES, "job_types": JOB_TYPES, "today": date.today().isoformat()}

@bp.route("/")
def dashboard():
    db = get_db()
    stats = db.execute("""
        SELECT COUNT(*) AS total,
        SUM(CASE WHEN status='Applied' THEN 1 ELSE 0 END) AS applied,
        SUM(CASE WHEN status='Interview' THEN 1 ELSE 0 END) AS interviews,
        SUM(CASE WHEN status='Offer' THEN 1 ELSE 0 END) AS offers,
        SUM(CASE WHEN status='Rejected' THEN 1 ELSE 0 END) AS rejected
        FROM applications
    """).fetchone()
    recent = db.execute("SELECT * FROM applications ORDER BY updated_at DESC, id DESC LIMIT 6").fetchall()
    by_status = db.execute("SELECT status, COUNT(*) AS count FROM applications GROUP BY status").fetchall()
    followups = db.execute("""
        SELECT * FROM applications
        WHERE follow_up_on <> '' AND follow_up_on <= ?
          AND status NOT IN ('Offer','Rejected','Withdrawn')
        ORDER BY follow_up_on ASC LIMIT 5
    """, (date.today().isoformat(),)).fetchall()
    return render_template("dashboard.html", stats=stats, recent=recent,
                           by_status={r["status"]: r["count"] for r in by_status},
                           followups=followups)

@bp.route("/applications")
def applications():
    q = clean(request.args.get("q"), 100)
    status = clean(request.args.get("status"), 30)
    db = get_db()
    sql = "SELECT * FROM applications WHERE 1=1"
    params = []
    if q:
        sql += " AND (company LIKE ? OR role LIKE ? OR location LIKE ?)"
        params.extend([f"%{q}%"] * 3)
    if status in STATUSES:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY updated_at DESC, id DESC"
    rows = db.execute(sql, params).fetchall()
    return render_template("applications.html", applications=rows, q=q, selected_status=status)

def save_form(row=None):
    data = {
        "company": clean(request.form.get("company"), 120),
        "role": clean(request.form.get("role"), 120),
        "location": clean(request.form.get("location"), 120),
        "job_type": clean(request.form.get("job_type"), 30) or "Full-time",
        "source": clean(request.form.get("source"), 120),
        "job_url": clean(request.form.get("job_url"), 500),
        "salary": clean(request.form.get("salary"), 80),
        "status": clean(request.form.get("status"), 30) or "Saved",
        "applied_on": clean(request.form.get("applied_on"), 10),
        "follow_up_on": clean(request.form.get("follow_up_on"), 10),
        "contact_name": clean(request.form.get("contact_name"), 120),
        "contact_email": clean(request.form.get("contact_email"), 160),
        "notes": clean(request.form.get("notes"), 5000),
    }
    if not data["company"] or not data["role"]:
        flash("Company and role are required.", "error")
        return None
    if data["status"] not in STATUSES:
        data["status"] = "Saved"
    if data["job_type"] not in JOB_TYPES:
        data["job_type"] = "Full-time"
    if data["job_url"] and not data["job_url"].startswith(("https://", "http://")):
        flash("Job URL must begin with http:// or https://.", "error")
        return None
    return data

@bp.route("/applications/new", methods=["GET", "POST"])
def new_application():
    if request.method == "POST":
        data = save_form()
        if data:
            db = get_db()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            db.execute(f"INSERT INTO applications ({columns}) VALUES ({placeholders})", list(data.values()))
            db.commit()
            flash("Application added to your tracker.", "success")
            return redirect(url_for("main.applications"))
    return render_template("application_form.html", application=None, page_title="Add application")

@bp.route("/applications/<int:app_id>")
def detail(app_id):
    application = get_application(app_id)
    return render_template("detail.html", application=application)

@bp.route("/applications/<int:app_id>/edit", methods=["GET", "POST"])
def edit_application(app_id):
    application = get_application(app_id)
    if request.method == "POST":
        data = save_form(application)
        if data:
            assignments = ", ".join(f"{key} = ?" for key in data)
            get_db().execute(
                f"UPDATE applications SET {assignments}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                list(data.values()) + [app_id]
            )
            get_db().commit()
            flash("Application updated.", "success")
            return redirect(url_for("main.detail", app_id=app_id))
    return render_template("application_form.html", application=application, page_title="Edit application")

@bp.route("/applications/<int:app_id>/delete", methods=["POST"])
def delete_application(app_id):
    get_application(app_id)
    get_db().execute("DELETE FROM applications WHERE id=?", (app_id,))
    get_db().commit()
    flash("Application deleted.", "success")
    return redirect(url_for("main.applications"))

@bp.route("/applications/<int:app_id>/status", methods=["POST"])
def update_status(app_id):
    get_application(app_id)
    status = clean(request.form.get("status"), 30)
    if status not in STATUSES:
        flash("Choose a valid status.", "error")
    else:
        get_db().execute("UPDATE applications SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                         (status, app_id))
        get_db().commit()
        flash("Status updated.", "success")
    return redirect(request.referrer or url_for("main.applications"))

@bp.route("/export.csv")
def export_csv():
    rows = get_db().execute("SELECT * FROM applications ORDER BY created_at DESC").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = rows[0].keys() if rows else [
        "id", "company", "role", "location", "job_type", "source", "job_url",
        "salary", "status", "applied_on", "follow_up_on", "contact_name",
        "contact_email", "notes", "created_at", "updated_at"
    ]
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row[h] for h in headers])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=job-applications.csv"})

@bp.route("/tools/resume-match", methods=["GET", "POST"])
def resume_match():
    result = None
    if request.method == "POST":
        resume_text = clean(request.form.get("resume_text"), 30000)
        job_text = clean(request.form.get("job_text"), 30000)
        if not resume_text or not job_text:
            flash("Paste both your resume text and the job description.", "error")
        else:
            result = compare_keywords(resume_text, job_text)
    return render_template("resume_match.html", result=result)
