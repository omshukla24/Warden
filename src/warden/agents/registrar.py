from warden.models import CapabilityManifest, VettingVerdict, RegistryEntry, ProvenanceEvent, AuditEvent, utcnow_iso
from warden.crypto.signing import canonicalize, sign
from warden.store.firestore_repo import next_version, write_registry_entry, get_latest_registry_entry, update_registry_entry, append_audit_event
from warden.telemetry.otel import span, get_trace_id
import os

def _get_private_key() -> bytes:
    key = os.environ.get("SIGNING_KEY_PEM")
    if key:
        return key.encode('utf-8')
    from google.cloud import secretmanager
    from warden.config import GCP_PROJECT_ID, SIGNING_KEY_SECRET
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{GCP_PROJECT_ID}/secrets/{SIGNING_KEY_SECRET}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data

def on_verdict(manifest: CapabilityManifest, verdict: VettingVerdict) -> RegistryEntry:
    with span("Registrar.on_verdict"):
        now = utcnow_iso()
        trace_id = get_trace_id()
        
        submitted_event = ProvenanceEvent(event="SUBMITTED", at=manifest.submitted_at, detail=f"By {manifest.submitted_by_agent}")
        vetted_event = ProvenanceEvent(event="VETTED", at=now, detail=f"Verdict: {verdict.decision}. Risk: {verdict.risk_score}")
        
        version = next_version(manifest.capability_id)
        
        if verdict.decision == "APPROVE":
            canonical = canonicalize(manifest, verdict)
            sig = sign(canonical, _get_private_key())
            
            signed_event = ProvenanceEvent(event="SIGNED", at=now, detail="warden-registrar")
            
            entry = RegistryEntry(
                capability_id=manifest.capability_id,
                manifest=manifest,
                verdict=verdict,
                status="APPROVED",
                signature=sig,
                signed_by="warden-registrar",
                provenance=[submitted_event, vetted_event, signed_event],
                version=version,
                created_at=now,
                updated_at=now
            )
            write_registry_entry(entry)

            audit = AuditEvent(
                event_id=f"audit-{manifest.capability_id}-{now}",
                event_type="REGISTRATION_SEALED",
                capability_id=manifest.capability_id,
                invoking_agent=manifest.submitted_by_agent,
                decision="ALLOW",
                reason=(verdict.summary or "Signature valid — sealed to the registry."),
                signature_valid=True,
                model_armor_result=None,
                trace_id=trace_id,
                timestamp=now
            )
            append_audit_event(audit)
            return entry
        else:
            # BLOCK or QUARANTINE
            rejected_event = ProvenanceEvent(event="REJECTED", at=now, detail=verdict.summary)
            entry = RegistryEntry(
                capability_id=manifest.capability_id,
                manifest=manifest,
                verdict=verdict,
                status="REJECTED",
                signature=None,
                signed_by=None,
                provenance=[submitted_event, vetted_event, rejected_event],
                version=version,
                created_at=now,
                updated_at=now
            )
            write_registry_entry(entry)
            
            audit = AuditEvent(
                event_id=f"audit-{manifest.capability_id}-{now}",
                event_type="REGISTRATION_BLOCKED",
                capability_id=manifest.capability_id,
                invoking_agent=manifest.submitted_by_agent,
                decision="BLOCK",
                reason=verdict.summary,
                signature_valid=None,
                model_armor_result=None,
                trace_id=trace_id,
                timestamp=now
            )
            append_audit_event(audit)
            return entry

def revoke(capability_id: str, reason: str):
    with span("Registrar.revoke"):
        entry = get_latest_registry_entry(capability_id)
        if not entry:
            return
            
        now = utcnow_iso()
        trace_id = get_trace_id()
        
        entry.status = "REVOKED"
        entry.provenance.append(ProvenanceEvent(event="REVOKED", at=now, detail=reason))
        entry.updated_at = now
        
        update_registry_entry(entry)
        
        audit = AuditEvent(
            event_id=f"audit-revoke-{capability_id}-{now}",
            event_type="CAPABILITY_REVOKED",
            capability_id=capability_id,
            invoking_agent="warden-sweeper",
            decision="BLOCK",
            reason=reason,
            signature_valid=None,
            model_armor_result=None,
            trace_id=trace_id,
            timestamp=now
        )
        append_audit_event(audit)
