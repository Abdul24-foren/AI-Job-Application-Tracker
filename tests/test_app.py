import os
import tempfile
import unittest
from app import create_app

class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp.name, "test.sqlite3")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-secret",
                               "DATABASE": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CareerFlow", response.data)

    def test_create_and_view_application(self):
        response = self.client.post("/applications/new", data={
            "company": "Acme", "role": "Python Developer", "status": "Applied"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Acme", response.data)
        self.assertIn(b"Python Developer", response.data)

    def test_validation_rejects_missing_company(self):
        response = self.client.post("/applications/new", data={
            "company": "", "role": "Developer"
        }, follow_redirects=True)
        self.assertIn(b"Company and role are required", response.data)

    def test_invalid_job_url_is_rejected(self):
        response = self.client.post("/applications/new", data={
            "company": "Acme", "role": "Developer", "job_url": "javascript:alert(1)"
        }, follow_redirects=True)
        self.assertIn(b"Job URL must begin", response.data)

    def test_search_and_status_filter(self):
        self.client.post("/applications/new", data={
            "company": "Northstar", "role": "Engineer", "status": "Interview"
        })
        response = self.client.get("/applications?q=Northstar&status=Interview")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Northstar", response.data)

    def test_csv_export(self):
        response = self.client.get("/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.content_type)

    def test_resume_match(self):
        response = self.client.post("/tools/resume-match", data={
            "resume_text": "Python Flask SQL Docker",
            "job_text": "Python developer with Flask SQL and Docker experience"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your keyword alignment", response.data)

if __name__ == "__main__":
    unittest.main()
