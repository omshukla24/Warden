import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from warden.crypto.signing import canonicalize, sign, verify
from warden.models import CapabilityManifest, VettingVerdict, Finding

@pytest.fixture
def keypair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

@pytest.fixture
def sample_data():
    manifest = CapabilityManifest(
        capability_id="cap-123",
        name="test-tool",
        type="tool",
        description="A test tool",
        provider="internal",
        version="1.0.0",
        requested_scopes=["read:files"],
        raw_definition="{}",
        submitted_by_agent="agent-01",
        submitted_at="2025-01-01T00:00:00Z"
    )
    verdict = VettingVerdict(
        capability_id="cap-123",
        decision="APPROVE",
        risk_score=10,
        threat_classes=[],
        findings=[],
        summary="Looks good",
        model_used="gemini-3.5-flash",
        vetted_at="2025-01-01T00:01:00Z"
    )
    return manifest, verdict

def test_sign_verify_roundtrip(keypair, sample_data):
    priv, pub = keypair
    manifest, verdict = sample_data
    
    canonical = canonicalize(manifest, verdict)
    sig = sign(canonical, priv)
    
    assert verify(canonical, sig, pub) is True

def test_verify_tampered_manifest(keypair, sample_data):
    priv, pub = keypair
    manifest, verdict = sample_data
    
    canonical_orig = canonicalize(manifest, verdict)
    sig = sign(canonical_orig, priv)
    
    # Mutate manifest
    manifest.description = "A tampered description"
    canonical_tampered = canonicalize(manifest, verdict)
    
    assert verify(canonical_tampered, sig, pub) is False

def test_verify_wrong_key(keypair, sample_data):
    priv, _ = keypair
    
    wrong_private_key = ed25519.Ed25519PrivateKey.generate()
    wrong_pub_pem = wrong_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    manifest, verdict = sample_data
    canonical = canonicalize(manifest, verdict)
    sig = sign(canonical, priv)
    
    assert verify(canonical, sig, wrong_pub_pem) is False

def test_canonicalization_is_stable(sample_data):
    manifest, verdict = sample_data
    c1 = canonicalize(manifest, verdict)
    
    # recreate identical objects
    m2 = CapabilityManifest(**manifest.model_dump())
    v2 = VettingVerdict(**verdict.model_dump())
    c2 = canonicalize(m2, v2)
    
    assert c1 == c2
