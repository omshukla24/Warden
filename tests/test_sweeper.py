import pytest
from warden.sweeper.sweeper import on_sweep
from warden.models import CapabilityManifest, VettingVerdict, RegistryEntry

@pytest.fixture
def mock_dependencies(monkeypatch):
    store = []
    revoked = []
    
    def m_get_all():
        return store
        
    def m_revoke(cid, reason):
        revoked.append((cid, reason))
        
    def m_vet(manifest):
        if "bad" in manifest.description:
            return VettingVerdict(decision="BLOCK", findings=[], summary="now unsafe", risk_score=100, threat_classes=["mock"], capability_id=manifest.capability_id, model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
        return VettingVerdict(decision="APPROVE", findings=[], summary="safe", risk_score=0, threat_classes=[], capability_id=manifest.capability_id, model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
        
    monkeypatch.setattr("warden.sweeper.sweeper.get_all_approved_entries", m_get_all)
    monkeypatch.setattr("warden.sweeper.sweeper.revoke", m_revoke)
    monkeypatch.setattr("warden.sweeper.sweeper.vet_capability", m_vet)
    
    return store, revoked

def create_entry(cid, desc="safe"):
    manifest = CapabilityManifest(
        capability_id=cid, name="test", type="tool", description=desc, provider="test",
        version="1.0", requested_scopes=[], raw_definition="{}", submitted_by_agent="a", submitted_at="2025-01-01T00:00:00Z"
    )
    return RegistryEntry(
        capability_id=cid, manifest=manifest, verdict=VettingVerdict(decision="APPROVE", findings=[], summary="ok", risk_score=0, threat_classes=[], capability_id=cid, model_used="gemini", vetted_at="2025-01-01T00:00:00Z"),
        status="APPROVED", signature="mock-sig", signed_by="test", provenance=[], version=1,
        created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z"
    )

def test_sweeper_revokes_unsafe(mock_dependencies):
    store, revoked = mock_dependencies
    store.append(create_entry("cap-1", "safe"))
    store.append(create_entry("cap-2", "bad stuff discovered later"))
    
    res = on_sweep()
    assert res["checked"] == 2
    assert "cap-2" in res["revoked"]
    assert "cap-1" not in res["revoked"]
    assert len(revoked) == 1
    assert revoked[0][0] == "cap-2"
    assert "re-vet failed" in revoked[0][1]

def test_sweeper_idempotent(mock_dependencies):
    store, revoked = mock_dependencies
    store.append(create_entry("cap-1", "safe"))
    
    res1 = on_sweep()
    res2 = on_sweep()
    assert res1["revoked"] == []
    assert res2["revoked"] == []
    assert len(revoked) == 0

def test_sweeper_empty_registry(mock_dependencies):
    res = on_sweep()
    assert res["checked"] == 0
    assert res["revoked"] == []

def test_sweeper_multiple_revocations(mock_dependencies):
    store, revoked = mock_dependencies
    store.append(create_entry("cap-bad-1", "bad item 1"))
    store.append(create_entry("cap-good-1", "safe item"))
    store.append(create_entry("cap-bad-2", "bad item 2"))
    
    res = on_sweep()
    assert res["checked"] == 3
    assert len(res["revoked"]) == 2
    assert "cap-bad-1" in res["revoked"]
    assert "cap-bad-2" in res["revoked"]
    assert len(revoked) == 2
