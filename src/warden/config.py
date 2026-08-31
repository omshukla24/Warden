import os

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "local-test-project")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")
MODEL_ID = os.environ.get("MODEL_ID", "gemini-3.5-flash")
GEMMA_MODEL_ID = os.environ.get("GEMMA_MODEL_ID", "gemma-2-9b-it")
GEMMA_ENABLED = os.environ.get("GEMMA_ENABLED", "true").lower() == "true"

# Route the Google GenAI SDK / ADK to Vertex AI (uses gcloud ADC — no API key).
# Gemini 3.x models on Vertex are ONLY served on the global endpoint, not regional (us-central1).
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", GCP_PROJECT_ID)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
FIRESTORE_COLLECTION_REGISTRY = os.environ.get("FIRESTORE_COLLECTION_REGISTRY", "warden_registry")
FIRESTORE_COLLECTION_AUDIT = os.environ.get("FIRESTORE_COLLECTION_AUDIT", "warden_audit")
MODEL_ARMOR_TEMPLATE = os.environ.get("MODEL_ARMOR_TEMPLATE", "warden-armor")
SIGNING_KEY_SECRET = os.environ.get("SIGNING_KEY_SECRET", "warden-ed25519-private")
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "warden-sweep")

