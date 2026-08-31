from warden.models import CapabilityManifest, RegistryEntry
from warden.agents.inspector import vet_capability
from warden.agents.gemma_screener import screen_with_gemma_sync
from warden.agents.registrar import on_verdict
from warden.telemetry.otel import span


def register_capability(manifest: CapabilityManifest) -> RegistryEntry:
    with span("Orchestrator.register_capability"):
        # 1. Fast first-pass screen with Gemma 2 (open-weights, Gemini Developer API).
        gemma_result = screen_with_gemma_sync(manifest)

        # 2. Deep OWASP LLM Top 10 analysis with Gemini 3.5 Flash (Vertex AI).
        verdict = vet_capability(manifest)

        # 3. Record the Gemma pre-screen on the verdict so it is persisted to the
        #    registry, returned by the API, and visible in the dashboard + audit.
        #    (verdict.summary is NOT part of the Ed25519 canonical signature, so
        #    this is safe to annotate.)
        verdict.prescreen = gemma_result.model_dump()
        tag = (
            f"[Gemma 2 pre-screen: "
            f"{'SUSPICIOUS' if gemma_result.is_suspicious else 'clean'} "
            f"· risk {gemma_result.preliminary_risk} · {gemma_result.screened_by}] "
        )
        verdict.summary = (tag + (verdict.summary or "")).strip()

        # 4. Cryptographic signing and registry storage.
        entry = on_verdict(manifest, verdict)
        return entry
