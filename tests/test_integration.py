import pytest
from fastapi.testclient import TestClient
from warden.api.main import app

client = TestClient(app)

@pytest.fixture
def mock_all(monkeypatch):
    store = {}
    
    def m_vet(manifest):
        if "bad" in manifest.description:
            from warden.models import VettingVerdict
            return VettingVerdict(decision="BLOCK", findings=[], summary="unsafe", risk_score=100, threat_classes=["mock"], capability_id=manifest.capability_id, model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
        from warden.models import VettingVerdict
        return VettingVerdict(decision="APPROVE", findings=[], summary="safe", risk_score=0, threat_classes=[], capability_id=manifest.capability_id, model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
        
    def m_get(cid):
        return store.get(cid)
        
    def m_write(entry):
        store[entry.capability_id] = entry
        
    def m_update(entry):
        store[entry.capability_id] = entry
        
    def m_next_version(cid):
        return 1
        
    def m_get_all_approved():
        return [e for e in store.values() if e.status == "APPROVED"]
        
    monkeypatch.setattr("warden.agents.orchestrator.vet_capability", m_vet)
    monkeypatch.setattr("warden.agents.registrar.write_registry_entry", m_write)
    monkeypatch.setattr("warden.agents.registrar.get_latest_registry_entry", m_get)
    monkeypatch.setattr("warden.agents.registrar.update_registry_entry", m_update)
    monkeypatch.setattr("warden.agents.registrar.next_version", m_next_version)
    
    monkeypatch.setattr("warden.agents.gatekeeper.get_latest_registry_entry", m_get)
    monkeypatch.setattr("warden.agents.gatekeeper.append_audit_event", lambda x: None)
    monkeypatch.setattr("warden.agents.registrar.append_audit_event", lambda x: None)
    monkeypatch.setattr("warden.agents.gatekeeper.model_armor.screen", lambda x: {"blocked": False, "categories": []})
    
    monkeypatch.setattr("warden.sweeper.sweeper.get_all_approved_entries", m_get_all_approved)
    monkeypatch.setattr("warden.sweeper.sweeper.vet_capability", m_vet)
    monkeypatch.setattr("warden.api.main.get_latest_registry_entry", m_get)
    monkeypatch.setattr("warden.api.main.get_all_approved_entries", m_get_all_approved)
    
    return store

def test_integration_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_integration_clean_lifecycle(mock_all):
    # 1. Register clean
    manifest = {
        "capability_id": "cap-int-1", "name": "test", "type": "tool",
        "description": "safe tool", "provider": "test", "version": "1.0",
        "requested_scopes": [], "raw_definition": "{}", "submitted_by_agent": "a",
        "submitted_at": "2025-01-01T00:00:00Z"
    }
    res = client.post("/capabilities", json=manifest)
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVED"
    assert res.json()["signature"] is not None
    
    # 2. Invoke ALLOW
    res = client.post("/invoke", json={"capability_id": "cap-int-1", "invoking_agent": "a", "payload": "test"})
    assert res.json()["decision"] == "ALLOW"
    
    # 3. Fetch registry entry
    res = client.get("/registry/cap-int-1")
    assert res.status_code == 200
    assert res.json()["capability_id"] == "cap-int-1"

def test_integration_poisoned_lifecycle(mock_all):
    # 1. Register poisoned
    manifest = {
        "capability_id": "cap-int-2", "name": "test", "type": "tool",
        "description": "bad tool", "provider": "test", "version": "1.0",
        "requested_scopes": [], "raw_definition": "{}", "submitted_by_agent": "a",
        "submitted_at": "2025-01-01T00:00:00Z"
    }
    res = client.post("/capabilities", json=manifest)
    assert res.status_code == 200
    assert res.json()["status"] == "REJECTED"
    
    # 2. Invoke BLOCK
    res = client.post("/invoke", json={"capability_id": "cap-int-2", "invoking_agent": "a", "payload": "test"})
    assert res.json()["decision"] == "BLOCK"

def test_integration_revoke_lifecycle(mock_all):
    manifest = {
        "capability_id": "cap-int-3", "name": "test", "type": "tool",
        "description": "safe tool", "provider": "test", "version": "1.0",
        "requested_scopes": [], "raw_definition": "{}", "submitted_by_agent": "a",
        "submitted_at": "2025-01-01T00:00:00Z"
    }
    client.post("/capabilities", json=manifest)
    
    from warden.agents.registrar import revoke
    revoke("cap-int-3", "manual revoke")
    
    res = client.post("/invoke", json={"capability_id": "cap-int-3", "invoking_agent": "a", "payload": "test"})
    assert res.json()["decision"] == "BLOCK"

def test_integration_sweep_endpoint(mock_all):
    manifest = {
        "capability_id": "cap-int-4", "name": "test", "type": "tool",
        "description": "safe tool", "provider": "test", "version": "1.0",
        "requested_scopes": [], "raw_definition": "{}", "submitted_by_agent": "a",
        "submitted_at": "2025-01-01T00:00:00Z"
    }
    client.post("/capabilities", json=manifest)
    
    # Trigger sweep endpoint
    res = client.post("/sweep", json={})
    assert res.status_code == 200
    assert "checked" in res.json()
    assert "revoked" in res.json()

def test_integration_tampered_manifest_fails(mock_all):
    store = mock_all
    manifest = {
        "capability_id": "cap-int-5", "name": "test", "type": "tool",
        "description": "safe tool", "provider": "test", "version": "1.0",
        "requested_scopes": [], "raw_definition": "{}", "submitted_by_agent": "a",
        "submitted_at": "2025-01-01T00:00:00Z"
    }
    res = client.post("/capabilities", json=manifest)
    assert res.status_code == 200
    
    # Simulate an unauthorized backend tamper of the stored description
    entry = store["cap-int-5"]
    entry.manifest.description = "Tampered description after signing"
    
    # Gatekeeper should detect signature mismatch
    res = client.post("/invoke", json={"capability_id": "cap-int-5", "invoking_agent": "a", "payload": "test"})
    assert res.json()["decision"] == "BLOCK"
    assert "signature invalid" in res.json()["reason"]
