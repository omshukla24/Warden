import pytest
import datetime
from warden.models import CapabilityManifest, VettingVerdict, Finding
from warden.agents.registrar import on_verdict, revoke

@pytest.fixture
def clean_manifest():
    return CapabilityManifest(
        capability_id="cap-test-01",
        name="test-cap",
        type="tool",
        description="test",
        provider="test",
        version="1.0.0",
        requested_scopes=[],
        raw_definition="{}",
        submitted_by_agent="test-agent",
        submitted_at="2025-01-01T00:00:00Z"
    )

@pytest.fixture
def mock_firestore(monkeypatch):
    store = {}
    audit_store = []
    
    def m_next_version(cid):
        if cid not in store:
            return 1
        return store[cid].version + 1
        
    def m_write(entry):
        store[entry.capability_id] = entry
        
    def m_get(cid):
        return store.get(cid)
        
    def m_update(entry):
        store[entry.capability_id] = entry
        
    def m_append(audit):
        audit_store.append(audit)
        
    monkeypatch.setattr("warden.agents.registrar.next_version", m_next_version)
    monkeypatch.setattr("warden.agents.registrar.write_registry_entry", m_write)
    monkeypatch.setattr("warden.agents.registrar.get_latest_registry_entry", m_get)
    monkeypatch.setattr("warden.agents.registrar.update_registry_entry", m_update)
    monkeypatch.setattr("warden.agents.registrar.append_audit_event", m_append)
    
    return store, audit_store

def test_registrar_approve_creates_signed_entry(clean_manifest, mock_firestore):
    store, _ = mock_firestore
    verdict = VettingVerdict(
        decision="APPROVE",
        findings=[],
        summary="ok",
        risk_score=0,
        threat_classes=[],
        capability_id=clean_manifest.capability_id,
        model_used="test-model",
        vetted_at="2025-01-01T00:00:00Z"
    )
    
    entry = on_verdict(clean_manifest, verdict)
    assert entry.status == "APPROVED"
    assert entry.signature is not None
    assert entry.signed_by == "warden-registrar"
    assert entry.version == 1
    
    assert entry.capability_id in store
    assert len(entry.provenance) == 3
    assert entry.provenance[0].event == "SUBMITTED"
    assert entry.provenance[1].event == "VETTED"
    assert entry.provenance[2].event == "SIGNED"

def test_registrar_block_creates_rejected_entry(clean_manifest, mock_firestore):
    store, audit = mock_firestore
    verdict = VettingVerdict(
        decision="BLOCK",
        findings=[Finding(evidence="bad", location="n/a", rationale="bad", threat_class="LLM01_PROMPT_INJECTION", severity="critical", citation="mock")],
        summary="bad prompt injection",
        risk_score=100,
        threat_classes=["LLM01_PROMPT_INJECTION"],
        capability_id=clean_manifest.capability_id,
        model_used="test-model",
        vetted_at="2025-01-01T00:00:00Z"
    )
    
    entry = on_verdict(clean_manifest, verdict)
    assert entry.status == "REJECTED"
    assert entry.signature is None
    assert entry.signed_by is None
    assert len(audit) == 1
    assert audit[0].decision == "BLOCK"
    assert audit[0].event_type == "REGISTRATION_BLOCKED"
    assert entry.provenance[-1].event == "REJECTED"

def test_registrar_quarantine_creates_rejected_entry(clean_manifest, mock_firestore):
    store, audit = mock_firestore
    verdict = VettingVerdict(
        decision="QUARANTINE",
        findings=[],
        summary="ambiguous manifest structure",
        risk_score=60,
        threat_classes=[],
        capability_id=clean_manifest.capability_id,
        model_used="test-model",
        vetted_at="2025-01-01T00:00:00Z"
    )
    
    entry = on_verdict(clean_manifest, verdict)
    assert entry.status == "REJECTED"
    assert entry.signature is None
    assert len(audit) == 1
    assert audit[0].event_type == "REGISTRATION_BLOCKED"

def test_registrar_revoke(clean_manifest, mock_firestore):
    store, audit = mock_firestore
    verdict = VettingVerdict(decision="APPROVE", findings=[], summary="ok", risk_score=0, threat_classes=[], capability_id="cap-1", model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
    entry = on_verdict(clean_manifest, verdict)
    
    # Then revoke
    revoke(clean_manifest.capability_id, "discovered vulnerability")
    
    updated_entry = store[clean_manifest.capability_id]
    assert updated_entry.status == "REVOKED"
    assert updated_entry.provenance[-1].event == "REVOKED"
    
    # Check audit log — approval now also emits a REGISTRATION_SEALED event,
    # so the revoke is the most recent audit entry.
    assert len(audit) == 2
    assert audit[0].event_type == "REGISTRATION_SEALED"
    assert audit[-1].event_type == "CAPABILITY_REVOKED"
    assert audit[-1].reason == "discovered vulnerability"

def test_registrar_revoke_nonexistent_noop(mock_firestore):
    store, audit = mock_firestore
    # Should not raise exception
    revoke("nonexistent-cap-999", "does not exist")
    assert len(audit) == 0

def test_registrar_monotonic_versioning(clean_manifest, mock_firestore):
    verdict = VettingVerdict(decision="APPROVE", findings=[], summary="ok", risk_score=0, threat_classes=[], capability_id="cap-1", model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
    entry1 = on_verdict(clean_manifest, verdict)
    assert entry1.version == 1
    
    entry2 = on_verdict(clean_manifest, verdict)
    assert entry2.version == 2
    
def test_registrar_idempotency(clean_manifest, mock_firestore):
    store, _ = mock_firestore
    verdict = VettingVerdict(decision="APPROVE", findings=[], summary="ok", risk_score=0, threat_classes=[], capability_id="cap-1", model_used="gemini", vetted_at="2025-01-01T00:00:00Z")
    entry1 = on_verdict(clean_manifest, verdict)
    
    # The capability ID is the same, versions increment.
    entry2 = on_verdict(clean_manifest, verdict)
    assert entry2.version == 2
    assert store[clean_manifest.capability_id].version == 2
