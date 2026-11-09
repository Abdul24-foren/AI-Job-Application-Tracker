"""Lightweight, offline resume/job-description keyword comparison."""
import re
from collections import Counter

STOP_WORDS = {
    "and", "the", "for", "with", "you", "your", "are", "our", "this", "that",
    "will", "have", "has", "from", "into", "their", "they", "job", "role",
    "work", "years", "year", "using", "use", "ability", "skills", "skill",
    "experience", "required", "preferred", "strong", "good", "knowledge",
    "team", "including", "such", "must", "about", "who", "what", "all",
}

def tokenize(text):
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#.]{1,}", (text or "").lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]

def compare_keywords(resume_text, job_text, limit=30):
    resume = set(tokenize(resume_text))
    counts = Counter(tokenize(job_text))
    ranked = [word for word, _ in counts.most_common(limit)]
    matched = [word for word in ranked if word in resume]
    missing = [word for word in ranked if word not in resume]
    total = len(ranked)
    score = round((len(matched) / total) * 100) if total else 0
    return {"score": score, "matched": matched, "missing": missing, "total": total}
