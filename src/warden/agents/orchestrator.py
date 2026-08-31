from warden.models import CapabilityManifest, RegistryEntry
from warden.agents.inspector import vet_capability
from warden.agents.registrar import on_verdict
from warden.telemetry.otel import span

def register_capability(manifest: CapabilityManifest) -> RegistryEntry:
    with span("Orchestrator.register_capability"):
        verdict = vet_capability(manifest)
        entry = on_verdict(manifest, verdict)
        return entry
