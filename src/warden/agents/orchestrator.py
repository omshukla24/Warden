from warden.models import CapabilityManifest, RegistryEntry
from warden.agents.inspector import vet_capability
from warden.agents.gemma_screener import screen_with_gemma_sync
from warden.agents.registrar import on_verdict
from warden.telemetry.otel import span

def register_capability(manifest: CapabilityManifest) -> RegistryEntry:
    with span("Orchestrator.register_capability"):
        # 1. Fast heuristic pre-screening with Gemma 2
        gemma_result = screen_with_gemma_sync(manifest)
        
        # 2. Deep OWASP static analysis with Gemini 3.5 Flash
        verdict = vet_capability(manifest)
        
        # 3. Cryptographic signing and registry storage
        entry = on_verdict(manifest, verdict)
        return entry

