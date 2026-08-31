#!/bin/bash
set -e

PROJECT_ID="$(gcloud config get-value project)"
REGION="${GCP_REGION:-us-central1}"

echo "=== Deploying WARDEN to Cloud Run ==="
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"

gcloud run deploy warden-api \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION},MODEL_ID=gemini-3.5-flash,FIRESTORE_COLLECTION_REGISTRY=warden_registry,FIRESTORE_COLLECTION_AUDIT=warden_audit,MODEL_ARMOR_TEMPLATE=warden-armor,MODEL_ARMOR_ENABLED=false" \
  --set-secrets="SIGNING_KEY_PEM=warden-ed25519-private:latest,SIGNING_KEY_PUB_PEM=warden-ed25519-public:latest"

WARDEN_URL="$(gcloud run services describe warden-api --region "$REGION" --format='value(status.url)')"
echo ""
echo "=== Deployment Succeeded ==="
echo "WARDEN API URL: $WARDEN_URL"
echo "Testing health check:"
curl -fsSL "$WARDEN_URL/healthz"
echo ""
