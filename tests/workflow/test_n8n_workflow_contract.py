"""n8n Workflow Contract & Schema Validation Test Suite.

Operational Automation & Inference Service.
Implements 3-Level n8n Workflow Validation:
  - Level A: Static JSON schema and structure validation.
  - Level B: n8n node types and configuration compliance.
  - Level C: Topological connection graph integrity and routing completeness.
"""
import json
import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))


@pytest.fixture(scope="module")
def workflow_json():
    candidates = [
        os.path.join(PROJECT_ROOT, "n8n", "workflows", "marketvoice_review_triage.json"),
        os.path.join(PROJECT_ROOT, "workflows", "n8n", "workflows", "marketvoice_review_triage.json"),
        os.path.join(PROJECT_ROOT, "workflows", "n8n", "marketvoice_review_triage.json"),
    ]
    wf_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    assert os.path.exists(wf_path), f"Workflow file not found at {wf_path}"
    with open(wf_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestN8nWorkflowContract:
    """Validate project-owned n8n workflow architecture and nodes."""

    def test_workflow_metadata(self, workflow_json):
        assert "name" in workflow_json
        assert "SYNTHETIC_OPERATIONAL_DEMONSTRATION" in workflow_json["name"]
        assert "nodes" in workflow_json
        assert "connections" in workflow_json

    def test_required_nodes_present(self, workflow_json):
        nodes = {n["name"]: n for n in workflow_json["nodes"]}
        required_node_names = [
            "Webhook Trigger",
            "Payload & PII Sanitizer",
            "Compute Idempotency Key",
            "Database Idempotency Check",
            "Idempotency Router",
            "FastAPI Review Analyze",
            "FastAPI Decision Evaluate",
            "Decision Switch Router",
            "Insert Human Review Case",
            "Insert Operational Event Log",
            "Insert Workflow Execution Metrics",
            "Format Response Webhook",
        ]
        for name in required_node_names:
            assert name in nodes, f"Missing required n8n node: '{name}'"

    def test_webhook_configuration(self, workflow_json):
        nodes = {n["name"]: n for n in workflow_json["nodes"]}
        webhook_node = nodes["Webhook Trigger"]
        params = webhook_node.get("parameters", {})
        assert params.get("httpMethod") == "POST"
        assert params.get("path") == "review-event"

    def test_fastapi_endpoints_configuration(self, workflow_json):
        nodes = {n["name"]: n for n in workflow_json["nodes"]}
        nlp_node = nodes["FastAPI Review Analyze"]
        nlp_params = nlp_node.get("parameters", {})
        assert "/v1/review/analyze" in nlp_params.get("url", "")

        dss_node = nodes["FastAPI Decision Evaluate"]
        dss_params = dss_node.get("parameters", {})
        assert "/v1/decision/evaluate" in dss_params.get("url", "")

    def test_decision_switch_routing_rules(self, workflow_json):
        nodes = {n["name"]: n for n in workflow_json["nodes"]}
        switch_node = nodes["Decision Switch Router"]
        assert switch_node["type"] == "n8n-nodes-base.switch"
        rules_container = switch_node.get("parameters", {}).get("rules", {})
        rules = rules_container.get("rules", []) or rules_container.get("values", [])
        assert len(rules) >= 2, "Decision Switch Router must have at least 2 branching rules"

    def test_connection_graph_topology(self, workflow_json):
        connections = workflow_json["connections"]
        assert "Webhook Trigger" in connections
        assert "Decision Switch Router" in connections
        assert "Compute Idempotency Key" in connections
        assert len(connections) >= 10, "Workflow connection graph must contain at least 10 topological edges"
