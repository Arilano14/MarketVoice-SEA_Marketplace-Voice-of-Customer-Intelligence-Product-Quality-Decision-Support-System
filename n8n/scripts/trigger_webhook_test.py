"""Trigger and Test Local n8n Webhook with Synthetic Review Events.

MarketVoice SEA — Operational Testing Tool.
Posts synthetic review events (SYNTHETIC_P1..P4) to local n8n instance
and validates the returned routing decision and priority score.
"""
import json
import os
import sys
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
N8N_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(N8N_DIR)

LOCAL_FIXTURES = os.path.join(N8N_DIR, "fixtures", "sample_review_events.json")
GLOBAL_FIXTURES = os.path.join(PROJECT_ROOT, "data", "interim", "sample_review_events.json")
FIXTURES_PATH = LOCAL_FIXTURES if os.path.exists(LOCAL_FIXTURES) else GLOBAL_FIXTURES

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/review-event")
N8N_TEST_WEBHOOK_URL = os.getenv("N8N_TEST_WEBHOOK_URL", "http://localhost:5678/webhook-test/review-event")

def post_event(url: str, event_data: dict):
    req_body = json.dumps(event_data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return e.code, {"error": err_body}
    except Exception as e:
        return 0, {"error": str(e)}

def main():
    print("=" * 70)
    print("MarketVoice SEA — n8n Webhook Test Harness")
    print(f"Target URL: {N8N_WEBHOOK_URL}")
    print("=" * 70)

    if not os.path.exists(FIXTURES_PATH):
        print(f"[FAIL] Fixtures file missing at: {FIXTURES_PATH}")
        sys.exit(1)

    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    print(f"Loaded {len(fixtures)} synthetic review events.\n")

    for fix in fixtures:
        print(f">> Triggering: {fix['fixture_id']} ({fix['description']})")
        print(f"   Review: \"{fix['review_text']}\" [Rating: {fix['rating']}]")

        status_code, res = post_event(N8N_WEBHOOK_URL, fix)

        # Fallback to test webhook if production webhook isn't active
        if status_code == 404:
            print("   [INFO] Production webhook returned 404. Retrying on test webhook endpoint...")
            status_code, res = post_event(N8N_TEST_WEBHOOK_URL, fix)

        if status_code == 200:
            print(f"   [SUCCESS 200] Routed to: {res.get('routing_destination')} | PRS: {res.get('priority_score')} ({res.get('priority_tier')})")
            print(f"   Reason Codes: {res.get('reason_codes')}")
        else:
            print(f"   [HTTP {status_code}] Response / Error: {res}")
        print("-" * 70)

if __name__ == "__main__":
    main()
