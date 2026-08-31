# WARDEN

**Autonomous Capability Registry & Gatekeeper for Enterprise Agent Systems**

WARDEN is a security perimeter and capability registrar for autonomous AI agents. Before an agent can utilize tools, MCP servers, sub-agents, or external APIs, WARDEN inspects the capability definition for security threats (e.g. data exfiltration, prompt injection, excessive scope, unauthorized network egress), cryptographically signs approved capabilities using Ed25519 attestations, and enforces verified execution through runtime gatekeeping and continuous registry auditing.

---

## Key Features

- **Automated Capability Vetting**: Inspects tool schemas, MCP servers, and manifest definitions using LLM security inspectors (Vertex AI Gemini).
- **Cryptographic Attestations**: Approved capabilities are signed with Ed25519 wax-seal signatures and stored immutably in the capability registry.
- **Runtime Gatekeeper**: Enforces strict capability validation, signature verification, and payload policy matching on every invocation.
- **Live Perimeter & Membrane UI**: Real-time visualization of capability ingress, live policy verdicts, audit docket, and per-agent fleet management.
- **Continuous Auditing & Sweeper**: Periodic registry sweeps to identify and revoke compromised or poisoned capabilities.

---

## Architecture

```
[Agent Request] 
      │
      ▼
[Capability Manifest] ───► [WARDEN Inspector] ───► [Ed25519 Attestation & Registry]
                                 │                               │
                                 ▼                               ▼
                          [OWASP Findings]              [Runtime Gatekeeper]
                                                                 │
                                                                 ▼
                                                        [Execution Allowed]
```

- **Backend**: FastAPI, Python 3.12+, Google GenAI / Vertex AI, Google Cloud Firestore, Secret Manager, Cloud Run.
- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind/Vanilla CSS, Canvas visualizer.

---

## Project Structure

```
.
├── src/warden/             # Core Python package
│   ├── agents/             # Security inspector & sweeper agents
│   ├── api/                # FastAPI routes & endpoints
│   ├── gatekeeper/         # Runtime policy enforcement
│   ├── registrar/          # Capability registry & attestation signing
│   ├── store/              # Firestore & persistence layer
│   └── models.py           # Core Pydantic data models
├── frontend/               # Next.js perimeter dashboard & studio
├── tests/                  # Unit and integration test suite
├── deploy/                 # GCP Cloud Run deployment scripts
├── Dockerfile              # Container definition for backend
└── pyproject.toml          # Python project configuration
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Google Cloud SDK (`gcloud`) with Vertex AI and Firestore access

### Local Backend Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```

3. Run unit tests:
   ```bash
   pytest tests/ -m "not live"
   ```

4. Start API server:
   ```bash
   uvicorn warden.api.main:app --host 0.0.0.0 --port 8080 --reload
   ```

### Local Frontend Setup

1. Navigate to frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

---

## Deployment to Google Cloud Run

Deploy the backend and frontend services using Google Cloud Build and Cloud Run:

```bash
# 1. Deploy API backend
gcloud run deploy warden-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi

# 2. Deploy Dashboard frontend
gcloud run deploy warden-dashboard \
  --source frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi
```

---

## License

Apache 2.0
