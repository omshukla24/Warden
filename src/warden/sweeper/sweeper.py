from warden.store.firestore_repo import get_all_approved_entries
from warden.agents.inspector import vet_capability
from warden.agents.registrar import revoke
from warden.telemetry.otel import span

def on_sweep() -> dict:
    with span("Sweeper.on_sweep"):
        entries = get_all_approved_entries()
        revoked = []
        for entry in entries:
            fresh_verdict = vet_capability(entry.manifest)
            if fresh_verdict.decision != "APPROVE":
                reason = f"re-vet failed: {fresh_verdict.summary}"
                revoke(entry.capability_id, reason=reason)
                revoked.append(entry.capability_id)
        return {"revoked": revoked, "checked": len(entries)}
