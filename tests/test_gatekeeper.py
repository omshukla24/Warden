import pytest
from warden.models import CapabilityManifest, VettingVerdict, RegistryEntry
from warden.agents.gatekeeper import on_invoke, _get_public_key
from warden.crypto.signing import canonicalize, sign
import os

@pytest.fixture
def mock_dependencies(monkeypatch):
    store = {}
    audit_store = []
    
    def m_get(cid):
        return store.get(cid)
    
    def m_append(audit):
        audit_store.append(audit)
        
    def m_screen(payload):
        if "bad" in payload:
            return {"blocked": True, "categories": ["mock_bad"]}
        return {"blocked": False, "categories": []}
        
    monkeypatch.setattr("warden.agents.gatekeeper.get_latest_registry_entry", m_get)
    monkeypatch.setattr("warden.agents.gatekeeper.append_audit_event", m_append)
    monkeypatch.setattr("warden.agents.gatekeeper.model_armor.screen", m_screen)
    
    return store, audit_store

def create_entry(cid, status="APPROVED", scopes=None, risk=0, tamper=False, cap_type="tool"):
    if scopes is None:
        scopes = []
    manifest = CapabilityManifest(
        capability_id=cid, name="test", type=cap_type, description="test", provider="test",
        version="1.0", requested_scopes=scopes, raw_definition="{}", submitted_by_agent="a", submitted_at="2025-01-01T00:00:00Z"
    )
    verdict = VettingVerdict(
        capability_id=cid,
        decision="APPROVE",
        findings=[],
        summary="ok",
        risk_score=risk,
        threat_classes=[],
        model_used="gemini-3.5-flash",
        vetted_at="2025-01-01T00:00:00Z"
    )
    canonical = canonicalize(manifest, verdict)
    priv_key_pem = os.environ["SIGNING_KEY_PEM"].encode('utf-8')
    sig = sign(canonical, priv_key_pem)
    if tamper:
        sig = "invalid_base64_signature_tampered"
    return RegistryEntry(
        capability_id=cid, manifest=manifest, verdict=verdict, status=status,
        signature=sig, signed_by="warden-registrar", provenance=[], version=1,
        created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z"
    )

def test_gatekeeper_allow_signed_in_policy(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1", scopes=["read:files"])
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "ALLOW"
    assert len(audit) == 1
    assert audit[0].decision == "ALLOW"
    assert audit[0].signature_valid is True

def test_gatekeeper_block_unsigned(mock_dependencies):
    store, audit = mock_dependencies
    entry = create_entry("cap-1", scopes=["read:files"])
    entry.signature = None
    store["cap-1"] = entry
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "BLOCK"
    assert "signature invalid" in res["reason"]
    assert audit[0].event_type == "SIGNATURE_INVALID"

def test_gatekeeper_block_revoked(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1", status="REVOKED")
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "BLOCK"
    assert "not approved" in res["reason"]

def test_gatekeeper_block_tampered_sig(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1", tamper=True)
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "BLOCK"
    assert "signature invalid" in res["reason"]

def test_gatekeeper_block_not_found(mock_dependencies):
    store, audit = mock_dependencies
    res = on_invoke("non-existent-cap", "agent-x", "payload")
    assert res["decision"] == "BLOCK"
    assert "not approved / not in registry" in res["reason"]
    assert len(audit) == 1

def test_gatekeeper_block_wrong_type(mock_dependencies):
    store, audit = mock_dependencies
    entry = create_entry("cap-1")
    # Bypass pydantic validation for testing unexpected/forbidden type
    object.__setattr__(entry.manifest, "type", "forbidden_type")
    # Re-sign with the new object structure so type check is isolated
    canonical = canonicalize(entry.manifest, entry.verdict)
    entry.signature = sign(canonical, os.environ["SIGNING_KEY_PEM"].encode('utf-8'))
    store["cap-1"] = entry
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "BLOCK"
    assert "type not permitted" in res["reason"]

def test_gatekeeper_block_overscope(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1", scopes=["unauthorized_scope"])
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "BLOCK"
    assert "scope exceeds policy" in res["reason"]

def test_gatekeeper_block_over_risk(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1", risk=99)
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "BLOCK"
    assert "risk exceeds tolerance" in res["reason"]

def test_gatekeeper_model_armor_block(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1")
    
    res = on_invoke("cap-1", "agent-x", "bad payload with prompt injection")
    assert res["decision"] == "BLOCK"
    assert "model armor" in res["reason"]
    assert audit[0].event_type == "MODEL_ARMOR_BLOCK"
    assert audit[0].model_armor_result["blocked"] is True

def test_gatekeeper_audit_emitted_trace_id(mock_dependencies):
    store, audit = mock_dependencies
    store["cap-1"] = create_entry("cap-1")
    
    res = on_invoke("cap-1", "agent-x", "good payload")
    assert res["decision"] == "ALLOW"
    assert len(audit) == 1
    assert "trace_id" in res["audit_event"]

def test_gatekeeper_missing_public_key_raises(monkeypatch):
    monkeypatch.delenv("SIGNING_KEY_PUB_PEM", raising=False)
    with pytest.raises(RuntimeError, match="SIGNING_KEY_PUB_PEM not set"):
        _get_public_key()
