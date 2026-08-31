import uuid
import os
from typing import Optional
from warden.crypto.signing import canonicalize, verify
from warden.store.firestore_repo import get_latest_registry_entry, append_audit_event
from warden.models import IdentityPolicy, AuditEvent, utcnow_iso
from warden.security import model_armor
from warden.telemetry.otel import span, get_trace_id

def _get_public_key() -> bytes:
    key = os.environ.get("SIGNING_KEY_PUB_PEM")
    if not key:
        raise RuntimeError("SIGNING_KEY_PUB_PEM not set")
    return key.encode('utf-8')

def get_identity_policy(agent_identity: str) -> IdentityPolicy:
    return IdentityPolicy(
        agent_identity=agent_identity,
        allowed_capability_types=["tool", "mcp_server", "model", "api"],
        allowed_scopes=["read:files", "write:db", "network:egress", "exec:shell", "read:invoices"],
        max_risk_tolerance=50,
        environment="dev"
    )

def on_invoke(capability_id: str, invoking_agent: str, payload: str) -> dict:
    with span("Gatekeeper.on_invoke") as s:
        now = utcnow_iso()
        trace_id = get_trace_id()
        event_id = str(uuid.uuid4())
        
        def emit_block(reason: str, event_type: str = "INVOCATION_BLOCKED", signature_valid: Optional[bool] = None, armor_res: Optional[dict] = None):
            audit = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                capability_id=capability_id,
                invoking_agent=invoking_agent,
                decision="BLOCK",
                reason=reason,
                signature_valid=signature_valid,
                model_armor_result=armor_res,
                trace_id=trace_id,
                timestamp=now
            )
            append_audit_event(audit)
            return {"decision": "BLOCK", "reason": reason, "audit_event": audit.model_dump()}

        entry = get_latest_registry_entry(capability_id)
        if entry is None or entry.status != "APPROVED":
            return emit_block("not approved / not in registry")
            
        canonical = canonicalize(entry.manifest, entry.verdict)
        if not verify(canonical, entry.signature, _get_public_key()):
            return emit_block("signature invalid — tampered", "SIGNATURE_INVALID", signature_valid=False)
            
        policy = get_identity_policy(invoking_agent)
        
        if entry.manifest.type not in policy.allowed_capability_types:
            return emit_block("type not permitted", signature_valid=True)
            
        if not set(entry.manifest.requested_scopes).issubset(set(policy.allowed_scopes)):
            return emit_block("scope exceeds policy", signature_valid=True)
            
        if entry.verdict.risk_score > policy.max_risk_tolerance:
            return emit_block("risk exceeds tolerance", signature_valid=True)
            
        armor = model_armor.screen(payload)
        if armor["blocked"]:
            reason = "model armor: " + ", ".join(armor["categories"])
            return emit_block(reason, "MODEL_ARMOR_BLOCK", signature_valid=True, armor_res=armor)
            
        audit = AuditEvent(
            event_id=event_id,
            event_type="INVOCATION_ALLOWED",
            capability_id=capability_id,
            invoking_agent=invoking_agent,
            decision="ALLOW",
            reason="All checks passed",
            signature_valid=True,
            model_armor_result=armor,
            trace_id=trace_id,
            timestamp=now
        )
        append_audit_event(audit)
        return {"decision": "ALLOW", "reason": "All checks passed", "audit_event": audit.model_dump()}
