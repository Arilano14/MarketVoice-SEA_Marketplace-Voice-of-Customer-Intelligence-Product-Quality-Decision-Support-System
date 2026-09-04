"""MarketVoice SEA — n8n Comprehensive System & Operational Health Check.

Checks all system requirements, file dependencies, PostgreSQL operational tables,
FastAPI endpoints, port bindings, and workflow DAG integrity.
"""
import json
import os
import socket
import sqlite3
import subprocess
import sys
import urllib.request
import urllib.error

# Resolve paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
N8N_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(N8N_DIR)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def log_pass(msg: str):
    print(f" {GREEN}[PASS]{RESET} {msg}")

def log_warn(msg: str):
    print(f" {YELLOW}[WARN]{RESET} {msg}")

def log_fail(msg: str):
    print(f" {RED}[FAIL]{RESET} {msg}")

def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def main():
    print(f"\n{CYAN}================================================================={RESET}")
    print(f"{CYAN}   MarketVoice SEA — n8n System & Operational Health Audit        {RESET}")
    print(f"{CYAN}================================================================={RESET}")
    print(f"Workspace Directory: {N8N_DIR}\n")

    failures = 0
    warnings = 0

    # 1. Check Node.js
    print(f"{CYAN}[1/6] Runtime Environment (Node.js & npm){RESET}")
    try:
        node_res = subprocess.run(["node", "-v"], capture_output=True, text=True, check=True)
        node_ver = node_res.stdout.strip()
        log_pass(f"Node.js detected: {node_ver}")
    except Exception as e:
        log_fail(f"Node.js runtime not found in PATH: {e}")
        failures += 1

    try:
        npm_res = subprocess.run(["npm", "-v"], capture_output=True, text=True, check=True, shell=True)
        npm_ver = npm_res.stdout.strip()
        log_pass(f"npm detected: {npm_ver}")
    except Exception as e:
        log_warn(f"npm not found: {e}")
        warnings += 1

    # 2. Check File & Folder Dependencies
    print(f"\n{CYAN}[2/6] Workspace Structure & File Integrity{RESET}")
    required_files = [
        os.path.join(N8N_DIR, ".env"),
        os.path.join(N8N_DIR, ".env.example"),
        os.path.join(N8N_DIR, "package.json"),
        os.path.join(N8N_DIR, "docker-compose.yml"),
        os.path.join(N8N_DIR, "README.md"),
        os.path.join(N8N_DIR, "workflows", "marketvoice_review_triage.json"),
        os.path.join(N8N_DIR, "fixtures", "synthetic_p1_event.json"),
        os.path.join(N8N_DIR, "fixtures", "synthetic_p2_event.json"),
        os.path.join(N8N_DIR, "fixtures", "synthetic_p3_event.json"),
        os.path.join(N8N_DIR, "fixtures", "synthetic_p4_event.json"),
        os.path.join(N8N_DIR, "fixtures", "sample_review_events.json"),
        os.path.join(N8N_DIR, "scripts", "start_n8n.ps1"),
        os.path.join(N8N_DIR, "scripts", "start_n8n.sh"),
        os.path.join(N8N_DIR, "scripts", "trigger_webhook_test.py"),
        os.path.join(N8N_DIR, "scripts", "validate_workflow_syntax.py")
    ]
    missing_files = []
    for fpath in required_files:
        if os.path.exists(fpath):
            log_pass(f"Present: {os.path.relpath(fpath, N8N_DIR)}")
        else:
            log_fail(f"Missing required file: {os.path.relpath(fpath, N8N_DIR)}")
            missing_files.append(fpath)
            failures += 1

    # 3. Workflow DAG Integrity
    print(f"\n{CYAN}[3/6] Workflow DAG Validation{RESET}")
    wf_path = os.path.join(N8N_DIR, "workflows", "marketvoice_review_triage.json")
    if os.path.exists(wf_path):
        try:
            with open(wf_path, "r", encoding="utf-8") as f:
                wf_data = json.load(f)
            nodes = wf_data.get("nodes", [])
            node_types = {n.get("type") for n in nodes}
            log_pass(f"Valid JSON workflow '{wf_data.get('name')}' with {len(nodes)} nodes")
            
            # Check key nodes
            if "n8n-nodes-base.webhook" in node_types:
                log_pass("Webhook Trigger node verified")
            else:
                log_fail("Webhook Trigger node missing")
                failures += 1

            if "n8n-nodes-base.switch" in node_types or "n8n-nodes-base.if" in node_types:
                log_pass("Decision routing nodes verified")
            else:
                log_fail("Decision routing nodes missing")
                failures += 1

            if "n8n-nodes-base.postgres" in node_types:
                log_pass("PostgreSQL node verified")
            else:
                log_fail("PostgreSQL node missing")
                failures += 1
        except Exception as e:
            log_fail(f"Workflow JSON parsing error: {e}")
            failures += 1
    else:
        log_fail("Workflow file not found")
        failures += 1

    # 4. Local SQLite Persistence Check
    print(f"\n{CYAN}[4/6] Local n8n Persistence & SQLite DB{RESET}")
    db_path = os.path.join(N8N_DIR, "data", "database.sqlite")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
            tbl_count = cur.fetchone()[0]
            conn.close()
            log_pass(f"Local n8n SQLite DB operational ({tbl_count} tables initialized)")
        except Exception as e:
            log_warn(f"SQLite DB access error: {e}")
            warnings += 1
    else:
        log_warn("Local n8n SQLite DB will be auto-created upon first server launch")
        warnings += 1

    # 5. PostgreSQL Analytical Warehouse Connectivity
    print(f"\n{CYAN}[5/6] PostgreSQL Analytical Warehouse Connectivity{RESET}")
    pg_port_open = check_port("localhost", 5432)
    if pg_port_open:
        log_pass("PostgreSQL port 5432 is open and listening")
        # Try database query via psycopg
        try:
            import psycopg
            conn = psycopg.connect("postgresql://openpg:openpgpwd@localhost:5432/marketvoice_dev")
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM marketvoice_warehouse.fact_review")
            fact_count = cur.fetchone()[0]
            log_pass(f"Connected to 'marketvoice_dev' (fact_review contains {fact_count:,} records)")

            # Check operational tables
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'marketvoice_warehouse' 
                AND table_name IN ('operational_event_log', 'human_review_case')
            """)
            op_tables = [r[0] for r in cur.fetchall()]
            if len(op_tables) >= 2:
                log_pass(f"Operational tables verified in warehouse: {op_tables}")
            else:
                log_warn(f"Operational tables incomplete: found {op_tables}")
                warnings += 1
            conn.close()
        except Exception as e:
            log_warn(f"psycopg connection check warning: {e}")
            warnings += 1
    else:
        log_fail("PostgreSQL port 5432 is NOT open. Start PostgreSQL server.")
        failures += 1

    # 6. Service Port & External API Probes
    print(f"\n{CYAN}[6/6] External Services & Port Probes{RESET}")
    # Check FastAPI
    fastapi_port_open = check_port("localhost", 8000)
    if fastapi_port_open:
        try:
            req = urllib.request.Request("http://localhost:8000/health", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    log_pass("FastAPI microservice is RUNNING on http://localhost:8000 (status: 200)")
                else:
                    log_warn(f"FastAPI microservice returned HTTP {resp.status}")
                    warnings += 1
        except Exception as e:
            log_warn(f"FastAPI /health probe warning: {e}")
            warnings += 1
    else:
        log_warn("FastAPI microservice (port 8000) is currently offline.")
        print(f"        {YELLOW}-> Start it with: python scripts/runners/start_api.py{RESET}")
        warnings += 1

    # Check n8n Port
    n8n_port_open = check_port("localhost", 5678)
    if n8n_port_open:
        log_pass("n8n service is currently RUNNING on http://localhost:5678")
    else:
        log_pass("Port 5678 is available for n8n server binding")

    # Final Summary
    print(f"\n{CYAN}================================================================={RESET}")
    if failures == 0:
        print(f"{GREEN}   VERDICT: ALL CORE N8N SYSTEM REQUIREMENTS ARE MET (0 FAILURES){RESET}")
    else:
        print(f"{RED}   VERDICT: {failures} FAILURES DETECTED - PLEASE REVIEW LOGS ABOVE{RESET}")
    print(f"{CYAN}================================================================={RESET}\n")
    return failures

if __name__ == "__main__":
    sys.exit(main())
