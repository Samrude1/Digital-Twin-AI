"""
Test script to verify lead and question persistence in lead_manager.py
"""

import json
from pathlib import Path
import sys

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

from lead_manager import record_user, record_issue, LEADS_FILE, QUESTIONS_FILE

print("=" * 60)
print("TEST: Lead & Issue Persistence Verification")
print("=" * 60)

# Record test lead
lead_res = record_user(
    email="test.recruiter@example.com",
    name="Test Recruiter",
    notes="Interested in AI Architect role for Q3 2026",
)
print(f"record_user result: {lead_res}")
assert lead_res == {"status": "ok"}, "record_user must return {'status': 'ok'}"

# Verify file existence and content
assert LEADS_FILE.exists(), f"Expected {LEADS_FILE} to exist"
with LEADS_FILE.open("r", encoding="utf-8") as f:
    lines = [json.loads(line.strip()) for line in f if line.strip()]

matching_leads = [l for l in lines if l.get("email") == "test.recruiter@example.com"]
assert len(matching_leads) >= 1, "Expected test lead to be persisted in leads.jsonl"
saved_lead = matching_leads[-1]
print(f"✅ Lead verified in file: {saved_lead}")
assert saved_lead["name"] == "Test Recruiter"
assert "email_dispatched" in saved_lead

# Record test unknown question
issue_res = record_issue("Do you have experience with WebAssembly on edge devices?")
print(f"record_issue result: {issue_res}")
assert issue_res == {"status": "ok"}, "record_issue must return {'status': 'ok'}"

assert QUESTIONS_FILE.exists(), f"Expected {QUESTIONS_FILE} to exist"
with QUESTIONS_FILE.open("r", encoding="utf-8") as f:
    q_lines = [json.loads(line.strip()) for line in f if line.strip()]

matching_q = [q for q in q_lines if "WebAssembly" in q.get("question", "")]
assert len(matching_q) >= 1, "Expected test question to be persisted in unknown_questions.jsonl"
saved_q = matching_q[-1]
print(f"✅ Question verified in file: {saved_q}")
assert "email_dispatched" in saved_q

print("\n" + "=" * 60)
print("ALL PERSISTENCE TESTS PASSED SUCCESSFULLY!")
print("=" * 60)
