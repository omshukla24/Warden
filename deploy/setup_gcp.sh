#!/bin/bash
set -e

PROJECT_ID="$(gcloud config get-value project)"
REGION="${GCP_REGION:-us-central1}"

echo "=== WARDEN GCP Setup ==="
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"

echo "1. Enabling GCP Services..."
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  cloudtrace.googleapis.com \
  aiplatform.googleapis.com

echo "2. Setting up Secret Manager for Ed25519 Signing Keys..."
gcloud secrets create warden-ed25519-private --replication-policy="automatic" || true
gcloud secrets create warden-ed25519-public  --replication-policy="automatic" || true

if [ -f "warden_priv.pem" ]; then
  gcloud secrets versions add warden-ed25519-private --data-file="warden_priv.pem"
  echo "[+] Added warden-ed25519-private version from warden_priv.pem"
fi

if [ -f "warden_pub.pem" ]; then
  gcloud secrets versions add warden-ed25519-public --data-file="warden_pub.pem"
  echo "[+] Added warden-ed25519-public version from warden_pub.pem"
fi

echo "3. Granting IAM permissions to Cloud Run runtime service account..."
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for ROLE in roles/secretmanager.secretAccessor roles/datastore.user roles/aiplatform.user roles/modelarmor.user; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${RUNTIME_SA}" --role="$ROLE" || true
done

echo "=== Setup Complete ==="
