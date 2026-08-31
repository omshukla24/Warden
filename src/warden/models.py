import datetime
from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field


def utcnow_iso() -> str:
    """UTC timestamp in RFC 3339 / ISO 8601 form with a trailing 'Z'.

    Example: 2026-08-30T20:32:06.375000Z. Using a real 'Z' (not '+00:00Z')
    keeps the value parseable by JavaScript's Date() and other ISO parsers.
    """
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

class CapabilityManifest(BaseModel):
    capability_id: str
    name: str
    type: Literal["tool", "mcp_server", "model", "api"]
    description: str
    provider: str = "unknown"
    version: str = "1.0.0"
    endpoint: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    requested_scopes: List[str] = Field(default_factory=list)
    raw_definition: str = ""
    submitted_by_agent: str = "unknown"
    submitted_at: str = Field(default_factory=utcnow_iso)

class Finding(BaseModel):
    threat_class: str
    severity: Literal["critical", "high", "medium", "low"]
    evidence: str
    location: str
    rationale: str
    citation: str

class VettingVerdict(BaseModel):
    capability_id: Optional[str] = ""
    decision: Literal["APPROVE", "BLOCK", "QUARANTINE"]
    risk_score: int = 0
    threat_classes: List[str] = []
    findings: List[Finding] = []
    summary: str = ""
    model_used: Optional[str] = ""
    vetted_at: Optional[str] = ""

class ProvenanceEvent(BaseModel):
    event: Literal["SUBMITTED", "VETTED", "SIGNED", "REJECTED", "REVOKED"]
    at: str
    detail: str

class RegistryEntry(BaseModel):
    capability_id: str
    manifest: CapabilityManifest
    verdict: VettingVerdict
    status: Literal["APPROVED", "REJECTED", "REVOKED"]
    signature: Optional[str] = None
    signed_by: Optional[str] = None
    provenance: List[ProvenanceEvent]
    version: int
    created_at: str
    updated_at: str

class IdentityPolicy(BaseModel):
    agent_identity: str
    allowed_capability_types: List[str]
    allowed_scopes: List[str]
    max_risk_tolerance: int
    environment: Literal["prod", "staging", "dev"]

class AuditEvent(BaseModel):
    event_id: str
    event_type: Literal[
        "INVOCATION_ALLOWED",
        "INVOCATION_BLOCKED",
        "REGISTRATION_BLOCKED",
        "REGISTRATION_SEALED",
        "CAPABILITY_REVOKED",
        "MODEL_ARMOR_BLOCK",
        "SIGNATURE_INVALID"
    ]
    capability_id: str
    invoking_agent: Optional[str] = None
    decision: Literal["ALLOW", "BLOCK"]
    reason: str
    signature_valid: Optional[bool] = None
    model_armor_result: Optional[Dict[str, Any]] = None
    trace_id: str
    timestamp: str
