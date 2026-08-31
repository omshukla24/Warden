import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from warden.models import CapabilityManifest, VettingVerdict


def canonicalize(manifest: CapabilityManifest, verdict: VettingVerdict) -> bytes:
    """
    Deterministic JSON serialization (sorted keys, no whitespace, UTF-8)
    of capability_id, manifest(all fields), verdict.decision, verdict.risk_score, verdict.threat_classes
    """
    data = {
        "capability_id": manifest.capability_id,
        "manifest": manifest.model_dump(),
        "verdict": {
            "decision": verdict.decision,
            "risk_score": verdict.risk_score,
            "threat_classes": verdict.threat_classes,
        }
    }
    return json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')


def sign(canonical_bytes: bytes, private_key_pem: bytes) -> str:
    """Signs canonical bytes with ed25519 private key, returns base64 string."""
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    assert isinstance(private_key, ed25519.Ed25519PrivateKey)
    signature = private_key.sign(canonical_bytes)
    return base64.b64encode(signature).decode('utf-8')


def verify(canonical_bytes: bytes, signature_b64: str, public_key_pem: bytes) -> bool:
    """Verifies ed25519 signature against canonical bytes."""
    try:
        public_key = serialization.load_pem_public_key(public_key_pem)
        assert isinstance(public_key, ed25519.Ed25519PublicKey)
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, canonical_bytes)
        return True
    except Exception:
        return False
