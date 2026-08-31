from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from warden.models import RegistryEntry, AuditEvent
from warden.config import GCP_PROJECT_ID, FIRESTORE_COLLECTION_REGISTRY, FIRESTORE_COLLECTION_AUDIT
from typing import Optional, List

_db = None

def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=GCP_PROJECT_ID)
    return _db

def next_version(capability_id: str) -> int:
    # Equality-only query (auto-indexed) + max in Python. Avoids a composite
    # index so this works on any/new Firestore collection with zero setup.
    db = get_db()
    docs = db.collection(FIRESTORE_COLLECTION_REGISTRY).where(
        filter=FieldFilter("capability_id", "==", capability_id)
    ).stream()
    max_v = 0
    for doc in docs:
        v = doc.to_dict().get("version", 0) or 0
        if v > max_v:
            max_v = v
    return max_v + 1

def write_registry_entry(entry: RegistryEntry):
    db = get_db()
    doc_id = f"{entry.capability_id}_v{entry.version}"
    db.collection(FIRESTORE_COLLECTION_REGISTRY).document(doc_id).set(entry.model_dump())

def get_latest_registry_entry(capability_id: str) -> Optional[RegistryEntry]:
    # Equality-only query (auto-indexed) + highest version in Python — no
    # composite index needed, so it works on a fresh collection with no setup.
    db = get_db()
    docs = db.collection(FIRESTORE_COLLECTION_REGISTRY).where(
        filter=FieldFilter("capability_id", "==", capability_id)
    ).stream()
    latest: Optional[RegistryEntry] = None
    for doc in docs:
        entry = RegistryEntry(**doc.to_dict())
        if latest is None or entry.version > latest.version:
            latest = entry
    return latest

def update_registry_entry(entry: RegistryEntry):
    db = get_db()
    doc_id = f"{entry.capability_id}_v{entry.version}"
    db.collection(FIRESTORE_COLLECTION_REGISTRY).document(doc_id).set(entry.model_dump())

def append_audit_event(event: AuditEvent):
    db = get_db()
    db.collection(FIRESTORE_COLLECTION_AUDIT).document(event.event_id).set(event.model_dump())

def get_all_approved_entries() -> List[RegistryEntry]:
    db = get_db()
    docs = db.collection(FIRESTORE_COLLECTION_REGISTRY).where(
        filter=FieldFilter("status", "==", "APPROVED")
    ).stream()
    
    entries = []
    for doc in docs:
        entries.append(RegistryEntry(**doc.to_dict()))
    
    # Deduplicate by highest version
    latest_entries = {}
    for entry in entries:
        if entry.capability_id not in latest_entries or latest_entries[entry.capability_id].version < entry.version:
            latest_entries[entry.capability_id] = entry
            
    return list(latest_entries.values())

def get_all_entries() -> List[RegistryEntry]:
    """All capabilities on record (every status), deduplicated to the latest version each."""
    db = get_db()
    docs = db.collection(FIRESTORE_COLLECTION_REGISTRY).stream()
    latest = {}
    for doc in docs:
        entry = RegistryEntry(**doc.to_dict())
        if entry.capability_id not in latest or latest[entry.capability_id].version < entry.version:
            latest[entry.capability_id] = entry
    return list(latest.values())
