import pytest
import contextlib
import os

@pytest.fixture(autouse=True)
def disable_otel(monkeypatch):
    @contextlib.contextmanager
    def mock_span(*args, **kwargs):
        yield None
    monkeypatch.setattr("warden.telemetry.otel.span", mock_span)
    monkeypatch.setattr("warden.telemetry.otel.get_trace_id", lambda: "mock-trace-id")

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "local-test-project")
    # For crypto testing
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization as s
    k = ed25519.Ed25519PrivateKey.generate()
    priv = k.private_bytes(s.Encoding.PEM, s.PrivateFormat.PKCS8, s.NoEncryption())
    pub = k.public_key().public_bytes(s.Encoding.PEM, s.PublicFormat.SubjectPublicKeyInfo)
    monkeypatch.setenv("SIGNING_KEY_PEM", priv.decode('utf-8'))
    monkeypatch.setenv("SIGNING_KEY_PUB_PEM", pub.decode('utf-8'))
