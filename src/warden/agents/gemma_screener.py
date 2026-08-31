"""Gemma 2 Fast Pre-Screening Agent.

Runs Google's open-weights **Gemma 2** (`gemma-2-9b-it`) as a fast, low-cost first
pass over a capability manifest, ahead of the Gemini 3.5 Flash deep OWASP analysis.

Why the Gemini Developer API (not Vertex) for Gemma:
    Gemma is an open-weights model. On Vertex AI it is served only from a
    self-deployed Model Garden GPU/TPU endpoint, NOT from the managed
    `generateContent` path that serves Gemini. The Gemini Developer API
    (ai.google.dev), however, serves Gemma models directly by ID with a
    lightweight API key. So WARDEN calls Gemma there (key in GEMMA_API_KEY),
    while Gemini continues to run on Vertex AI via service-account ADC.

Honest degradation:
    If no key is configured, or the model call fails, we fall back to a fast
    local heuristic and label the result `screened_by="heuristic-fallback"` so
    it is always clear whether the real model ran. Gemma models on the Developer
    API do not support system instructions or JSON schema mode, so we put the
    instruction in the prompt and parse the JSON out of the text response.
"""

import os
import re
import json
from pydantic import BaseModel, Field
from warden.models import CapabilityManifest
from warden.config import GEMMA_MODEL_ID, GEMMA_ENABLED, GEMMA_API_KEY
from warden.telemetry.otel import span


class GemmaScreenResult(BaseModel):
    """Output from the Gemma 2 initial screening pass."""
    is_suspicious: bool = Field(default=False, description="True if the fast pass flags a likely risk")
    preliminary_risk: int = Field(default=0, ge=0, le=100, description="Preliminary 0-100 risk score")
    summary: str = Field(default="", description="Brief one-line reason")
    model: str = Field(default=GEMMA_MODEL_ID, description="Model identifier")
    screened_by: str = Field(default="gemma-2", description="'gemma-2' if the real model ran, else 'heuristic-fallback' / 'disabled'")


GEMMA_PROMPT = """You are a fast security pre-screener powered by Gemma 2.
Inspect the following AI tool / capability manifest for obvious red flags:
- prompt injection phrasing (e.g. "ignore previous instructions", hidden directives)
- data exfiltration (sending data to untrusted or external URLs)
- dangerous over-broad scopes (exec:shell, write:*, read:secrets, network:egress)

Respond with ONLY a JSON object, no prose, in exactly this shape:
{"is_suspicious": true or false, "preliminary_risk": 0-100, "summary": "one short line"}

MANIFEST:
"""


def _heuristic(manifest: CapabilityManifest) -> GemmaScreenResult:
    """Fast local rule check used when the real Gemma call is unavailable."""
    text = ((manifest.description or "") + " " + (manifest.raw_definition or "")).lower()
    scopes = str(manifest.requested_scopes).lower()
    injection = any(p in text for p in (
        "ignore previous", "ignore all previous", "disregard previous",
        "system prompt", "exfil",
    ))
    dangerous = any(d in scopes for d in ("exec:shell", "write:*", "read:secrets"))
    hit = injection or dangerous
    return GemmaScreenResult(
        is_suspicious=hit,
        preliminary_risk=85 if hit else 5,
        summary="Suspicious directive or over-broad scope detected" if hit else "No obvious red flags",
        model=GEMMA_MODEL_ID,
        screened_by="heuristic-fallback",
    )


def _parse_json(text: str):
    if not text:
        return None
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def screen_with_gemma_sync(manifest: CapabilityManifest) -> GemmaScreenResult:
    """Run the Gemma 2 fast pre-screen (synchronous entry point)."""
    with span("warden.gemma_screener.screen"):
        if not GEMMA_ENABLED:
            return GemmaScreenResult(
                is_suspicious=False, preliminary_risk=0,
                summary="Gemma screening disabled", model="disabled", screened_by="disabled",
            )
        if not GEMMA_API_KEY:
            # No Developer API key configured -> honest, clearly-labeled fallback.
            return _heuristic(manifest)
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=GEMMA_API_KEY)
            resp = client.models.generate_content(
                model=GEMMA_MODEL_ID,
                contents=GEMMA_PROMPT + manifest.model_dump_json(),
                config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=256),
            )
            data = _parse_json(getattr(resp, "text", "") or "")
            if data is not None:
                risk = int(data.get("preliminary_risk", 0) or 0)
                risk = max(0, min(100, risk))
                return GemmaScreenResult(
                    is_suspicious=bool(data.get("is_suspicious", False)),
                    preliminary_risk=risk,
                    summary=str(data.get("summary", ""))[:200],
                    model=GEMMA_MODEL_ID,
                    screened_by="gemma-2",
                )
        except Exception:
            pass
        # Any failure -> honest labeled fallback (never breaks the pipeline).
        return _heuristic(manifest)


async def screen_with_gemma(manifest: CapabilityManifest) -> GemmaScreenResult:
    """Async-compatible wrapper (kept for the existing test suite / callers)."""
    return screen_with_gemma_sync(manifest)
