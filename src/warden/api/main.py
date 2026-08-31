import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
from warden.models import CapabilityManifest
from warden.agents.orchestrator import register_capability
from warden.agents.gatekeeper import on_invoke
from warden.store.firestore_repo import get_all_approved_entries, get_all_entries, get_latest_registry_entry, get_db
from warden.sweeper.sweeper import on_sweep
from warden.config import FIRESTORE_COLLECTION_AUDIT

app = FastAPI(title="WARDEN", description="Software-supply-chain firewall for AI agents")

# CORS origins are configurable via WARDEN_CORS_ORIGINS (comma-separated).
# Default "*" keeps the dashboard working from any origin. Browsers reject a
# wildcard origin together with credentials, so credentials are only enabled
# when explicit origins are configured.
_cors_env = os.environ.get("WARDEN_CORS_ORIGINS", "*").strip()
_cors_origins = ["*"] if _cors_env in ("", "*") else [o.strip() for o in _cors_env.split(",") if o.strip()]
_allow_credentials = _cors_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/capabilities")
def create_capability(manifest: CapabilityManifest):
    entry = register_capability(manifest)
    return entry.model_dump()

@app.post("/invoke")
async def invoke_capability(request: Request):
    body = await request.json()
    cap_id = body.get("capability_id")
    agent = body.get("invoking_agent")
    payload = body.get("payload", "")
    if not cap_id:
        raise HTTPException(status_code=400, detail="capability_id is required")
    return on_invoke(cap_id, agent, payload)

@app.get("/registry")
def list_registry():
    # return every capability on record (approved, rejected, revoked) so the UI
    # can show blocked/voided data and the counters are accurate.
    entries = get_all_entries()
    return [e.model_dump() for e in entries]

@app.get("/registry/{capability_id}")
def get_registry_entry(capability_id: str):
    entry = get_latest_registry_entry(capability_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="capability not found")
    return entry.model_dump()

@app.get("/audit")
def get_audit(limit: int = 100):
    # Fetch + sort in Python (newest first) — no Firestore index dependency,
    # so this works on a brand-new/empty audit collection with zero setup.
    db = get_db()
    docs = db.collection(FIRESTORE_COLLECTION_AUDIT).stream()
    events = [d.to_dict() for d in docs]
    events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return events[:limit]

@app.post("/sweep")
def sweep():
    return on_sweep()

@app.get("/healthz")
@app.get("/health")
@app.get("/")
def healthz():
    return {"status": "ok"}

