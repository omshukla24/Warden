import os
from playwright.sync_api import sync_playwright

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WARDEN System Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --void: #07090e;
      --panel: #0f131f;
      --panel-border: rgba(255, 255, 255, 0.08);
      --bone: #f1f5f9;
      --dim: #94a3b8;
      --gold: #fde047;
      --gold-border: rgba(253, 224, 71, 0.4);
      --threat: #f43f5e;
      --threat-glow: rgba(244, 63, 94, 0.15);
      --seal: #10b981;
      --seal-glow: rgba(16, 185, 129, 0.15);
      --purple: #a855f7;
      --purple-glow: rgba(168, 85, 247, 0.15);
      --blue: #38bdf8;
      --blue-glow: rgba(56, 189, 248, 0.15);
      --gcp: #34d399;
      --grot: 'Space Grotesk', system-ui, sans-serif;
      --mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      width: 2560px;
      height: 1440px;
      background: var(--void);
      color: var(--bone);
      font-family: var(--grot);
      overflow: hidden;
      padding: 48px 64px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(168, 85, 247, 0.08), transparent 45%),
        radial-gradient(circle at 85% 15%, rgba(56, 189, 248, 0.08), transparent 45%),
        radial-gradient(circle at 50% 85%, rgba(16, 185, 129, 0.06), transparent 50%);
    }

    /* HEADER */
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--panel-border);
      padding-bottom: 24px;
    }

    .brand-title {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .brand-logo {
      font-size: 2.8rem;
    }

    .brand-title h1 {
      font-size: 2.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #fff;
    }

    .brand-title p {
      font-size: 1.15rem;
      color: var(--dim);
      margin-top: 4px;
    }

    .header-badges {
      display: flex;
      gap: 14px;
    }

    .badge {
      font-family: var(--mono);
      font-size: 0.85rem;
      font-weight: 600;
      padding: 8px 18px;
      border-radius: 999px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    .badge-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
    .badge-blue { background: rgba(56, 189, 248, 0.15); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-seal { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-gold { background: rgba(253, 224, 71, 0.12); color: var(--gold); border: 1px solid var(--gold-border); }

    /* MAIN ARCHITECTURE GRID */
    .arch-grid {
      display: grid;
      grid-template-columns: 460px 1fr 500px;
      gap: 36px;
      height: 980px;
      align-items: stretch;
    }

    .tier-column {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .tier-header {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 1.25rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--dim);
      padding-bottom: 8px;
      border-bottom: 1px solid var(--panel-border);
    }

    .tier-header span.icon { font-size: 1.4rem; }

    /* CARD STYLING */
    .arch-card {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
      display: flex;
      flex-direction: column;
      gap: 12px;
      position: relative;
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .card-title {
      font-size: 1.35rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .card-subtitle {
      font-family: var(--mono);
      font-size: 0.82rem;
      color: var(--dim);
    }

    .card-desc {
      font-size: 0.96rem;
      color: #cbd5e1;
      line-height: 1.5;
    }

    .card-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 4px;
    }

    .card-tag {
      font-family: var(--mono);
      font-size: 0.76rem;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--dim);
    }

    /* SPECIFIC TIER STYLES */
    .card-ingress { border-color: rgba(56, 189, 248, 0.3); }
    .card-ingress .card-tag { color: #38bdf8; border-color: rgba(56, 189, 248, 0.2); }

    .card-inspector {
      border-color: rgba(168, 85, 247, 0.4);
      box-shadow: 0 0 32px var(--purple-glow);
    }
    .card-inspector .card-title { color: #d8b4fe; }
    .card-inspector .card-tag { color: #c084fc; border-color: rgba(168, 85, 247, 0.3); }

    .card-registrar {
      border-color: rgba(16, 185, 129, 0.4);
      box-shadow: 0 0 32px var(--seal-glow);
    }
    .card-registrar .card-title { color: #6ee7b7; }
    .card-registrar .card-tag { color: #34d399; border-color: rgba(16, 185, 129, 0.3); }

    .card-gatekeeper {
      border-color: rgba(56, 189, 248, 0.4);
      box-shadow: 0 0 32px var(--blue-glow);
    }
    .card-gatekeeper .card-title { color: #7dd3fc; }
    .card-gatekeeper .card-tag { color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); }

    .card-sweeper {
      border-color: rgba(253, 224, 71, 0.3);
    }
    .card-sweeper .card-title { color: var(--gold); }
    .card-sweeper .card-tag { color: var(--gold); border-color: var(--gold-border); }

    .card-gcp {
      border-color: rgba(52, 211, 153, 0.3);
      background: rgba(15, 23, 42, 0.7);
    }
    .card-gcp .card-title { color: #6ee7b7; }
    .card-gcp .card-tag { color: #34d399; }

    /* MIDDLE MULTI-AGENT STACK */
    .middle-stack {
      display: grid;
      grid-template-rows: repeat(3, 1fr) 110px;
      gap: 16px;
      height: 100%;
    }

    /* RIGHT INFRASTRUCTURE STACK */
    .right-stack {
      display: grid;
      grid-template-rows: repeat(4, 1fr);
      gap: 16px;
      height: 100%;
    }

    /* BOTTOM SUMMARY BAR */
    footer {
      border-top: 2px solid var(--panel-border);
      padding-top: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--mono);
      font-size: 0.95rem;
      color: var(--dim);
    }

    .footer-stats {
      display: flex;
      gap: 32px;
    }

    .stat-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .stat-item strong {
      color: var(--gold);
    }
  </style>
</head>
<body>

  <!-- HEADER -->
  <header>
    <div class="brand-title">
      <div class="brand-logo">🛡️</div>
      <div>
        <h1>WARDEN: System Architecture & Separation-of-Duties</h1>
        <p>Autonomous Capability Registry & Cryptographic Gatekeeper for Enterprise Agent Fleets</p>
      </div>
    </div>
    <div class="header-badges">
      <div class="badge badge-purple">Google ADK Framework</div>
      <div class="badge badge-blue">Gemini 3.5 Flash</div>
      <div class="badge badge-seal">Ed25519 Attestations</div>
      <div class="badge badge-gold">Google Cloud Run</div>
    </div>
  </header>

  <!-- ARCHITECTURE GRID -->
  <div class="arch-grid">

    <!-- COLUMN 1: INGRESS & CLIENT LAYER -->
    <div class="tier-column">
      <div class="tier-header">
        <span class="icon">🖥️</span> Ingress & Client Layer
      </div>

      <!-- Card 1: Autonomous Agents -->
      <div class="arch-card card-ingress" style="flex: 1;">
        <div class="card-top">
          <div class="card-title">🤖 Agent Ingress</div>
          <div class="badge badge-blue">Client</div>
        </div>
        <div class="card-subtitle">Autonomous MCP Clients & Sub-Agents</div>
        <div class="card-desc">
          AI agents dynamically request external capabilities, third-party MCP servers, and tool definitions across enterprise boundaries.
        </div>
        <div class="card-tags">
          <div class="card-tag">Model Context Protocol (MCP)</div>
          <div class="card-tag">Tool Manifest Schemas</div>
          <div class="card-tag">Dynamic Ingress</div>
        </div>
      </div>

      <!-- Card 2: Next.js Dashboard -->
      <div class="arch-card card-ingress" style="flex: 1;">
        <div class="card-top">
          <div class="card-title">🌐 Perimeter UI</div>
          <div class="badge badge-blue">Next.js 16</div>
        </div>
        <div class="card-subtitle">Live Membrane & Vetting Studio</div>
        <div class="card-desc">
          Interactive console visualizing untrusted tokens traveling across the glowing protect line, batch JSON inspector, and live gatekeeper docket.
        </div>
        <div class="card-tags">
          <div class="card-tag">HTML5 Canvas (GridFX)</div>
          <div class="card-tag">Turbopack</div>
          <div class="card-tag">Ed25519 Wax-Seal SVG</div>
        </div>
      </div>

      <!-- Card 3: Enterprise Policy Engine -->
      <div class="arch-card card-ingress" style="flex: 0.85;">
        <div class="card-top">
          <div class="card-title">📜 Identity Matrix</div>
          <div class="badge badge-gold">Zero-Trust</div>
        </div>
        <div class="card-subtitle">Granular Agent Role Enforcement</div>
        <div class="card-desc">
          Defines per-agent allowed scopes and least-privilege boundary rules to stop capability overreach.
        </div>
        <div class="card-tags">
          <div class="card-tag">Scope Policies</div>
          <div class="card-tag">IAM Mapping</div>
        </div>
      </div>
    </div>

    <!-- COLUMN 2: WARDEN MULTI-AGENT CORE -->
    <div class="tier-column">
      <div class="tier-header">
        <span class="icon">🛡️</span> WARDEN Multi-Agent Core (Cloud Run Container)
      </div>

      <div class="middle-stack">

        <!-- Agent 1: Inspector -->
        <div class="arch-card card-inspector">
          <div class="card-top">
            <div class="card-title">🔍 1. The Inspector Agent</div>
            <div class="badge badge-purple">Gemini 3.5 Flash</div>
          </div>
          <div class="card-subtitle">Reasoning & OWASP LLM Taxonomy Scanner</div>
          <div class="card-desc">
            Deep static inspection of manifest descriptions, parameter definitions, and egress schemas against OWASP LLM01-LLM08. Extracts character-level citations and grounded threat evidence.
          </div>
          <div class="card-tags">
            <div class="card-tag">Vertex AI API</div>
            <div class="card-tag">Prompt-Injection Shield</div>
            <div class="card-tag">Data-Exfiltration Guard</div>
            <div class="card-tag">Scope Minimizer</div>
          </div>
        </div>

        <!-- Agent 2: Registrar -->
        <div class="arch-card card-registrar">
          <div class="card-top">
            <div class="card-title">🔏 2. The Registrar Agent</div>
            <div class="badge badge-seal">Ed25519 Signer</div>
          </div>
          <div class="card-subtitle">Hardware-Backed Cryptographic Minting</div>
          <div class="card-desc">
            Upon clean inspection, canonicalizes tool schemas and signs an immutable digital attestation with private keys stored in Secret Manager. Commits signed entries to Firestore.
          </div>
          <div class="card-tags">
            <div class="card-tag">Ed25519 Signatures</div>
            <div class="card-tag">Immutable Provenance</div>
            <div class="card-tag">Monotonic Versions</div>
            <div class="card-tag">Secret Manager</div>
          </div>
        </div>

        <!-- Agent 3: Gatekeeper -->
        <div class="arch-card card-gatekeeper">
          <div class="card-top">
            <div class="card-title">🛡️ 3. The Gatekeeper Agent</div>
            <div class="badge badge-blue">Runtime Enforcement</div>
          </div>
          <div class="card-subtitle">Zero-Trust Interception & Inline Armor</div>
          <div class="card-desc">
            Intercepts every tool call. Validates cryptographic signatures, verifies invoking agent identity policies, and passes parameters through Model Armor before execution.
          </div>
          <div class="card-tags">
            <div class="card-tag">Inline Signature Check</div>
            <div class="card-tag">Model Armor SDK</div>
            <div class="card-tag">Anti-Tamper Lock</div>
            <div class="card-tag">FastAPI Middleware</div>
          </div>
        </div>

        <!-- Component 4: Sweeper Daemon -->
        <div class="arch-card card-sweeper">
          <div class="card-top">
            <div class="card-title">⏰ 4. The Sweeper Daemon</div>
            <div class="badge badge-gold">Async Auditing</div>
          </div>
          <div class="card-desc" style="font-size: 0.88rem;">
            Continuously pulls active registry tools in background and re-audits manifests against updated threat heuristics to auto-revoke poisoned capabilities.
          </div>
        </div>

      </div>
    </div>

    <!-- COLUMN 3: GOOGLE CLOUD ENTERPRISE INFRASTRUCTURE -->
    <div class="tier-column">
      <div class="tier-header">
        <span class="icon">☁️</span> Google Cloud Infrastructure
      </div>

      <div class="right-stack">

        <!-- GCP 1: Vertex AI -->
        <div class="arch-card card-gcp">
          <div class="card-top">
            <div class="card-title">🧠 Vertex AI</div>
            <div class="badge badge-seal">AI Foundation</div>
          </div>
          <div class="card-subtitle">gemini-3.5-flash</div>
          <div class="card-desc">
            Low-latency structured reasoning engine providing deterministically formatted VettingVerdicts.
          </div>
          <div class="card-tags">
            <div class="card-tag">Region: us-central1</div>
            <div class="card-tag">Structured Outputs</div>
          </div>
        </div>

        <!-- GCP 2: Cloud Firestore -->
        <div class="arch-card card-gcp">
          <div class="card-top">
            <div class="card-title">🗄️ Cloud Firestore</div>
            <div class="badge badge-seal">NoSQL Database</div>
          </div>
          <div class="card-subtitle">Signed Registry & Live Audit Ledger</div>
          <div class="card-desc">
            Stores immutable capability catalogs (`warden_registry`) and streaming audit events (`warden_audit`).
          </div>
          <div class="card-tags">
            <div class="card-tag">Index-Free Equality Queries</div>
            <div class="card-tag">Audit Trail</div>
          </div>
        </div>

        <!-- GCP 3: Secret Manager & Model Armor -->
        <div class="arch-card card-gcp">
          <div class="card-top">
            <div class="card-title">🔐 Security Suite</div>
            <div class="badge badge-seal">Key Vault & Armor</div>
          </div>
          <div class="card-subtitle">Secret Manager + Model Armor</div>
          <div class="card-desc">
            Hardware-isolated Ed25519 signing keys and inline template guardrails against prompt injection and PII leaks.
          </div>
          <div class="card-tags">
            <div class="card-tag">warden-ed25519-private</div>
            <div class="card-tag">warden-armor</div>
          </div>
        </div>

        <!-- GCP 4: Serverless Eventing & Telemetry -->
        <div class="arch-card card-gcp">
          <div class="card-top">
            <div class="card-title">📊 Eventing & Trace</div>
            <div class="badge badge-seal">Cloud Native</div>
          </div>
          <div class="card-subtitle">Cloud Scheduler + Pub/Sub + Cloud Trace</div>
          <div class="card-desc">
            Automated cron heartbeats and distributed OpenTelemetry reasoning traces for every vetting decision.
          </div>
          <div class="card-tags">
            <div class="card-tag">Cloud Scheduler</div>
            <div class="card-tag">Pub/Sub Push</div>
            <div class="card-tag">Cloud Trace</div>
          </div>
        </div>

      </div>
    </div>

  </div>

  <!-- FOOTER -->
  <footer>
    <div>
      <span>WARDEN Architecture Blueprint</span> • <span>Production Ready on Google Cloud Run</span>
    </div>
    <div class="footer-stats">
      <div class="stat-item"><span>Status:</span> <strong>100% Deployed</strong></div>
      <div class="stat-item"><span>Test Suite:</span> <strong>47/47 Passed</strong></div>
      <div class="stat-item"><span>Attestation:</span> <strong>Ed25519 Wax Seal</strong></div>
      <div class="stat-item"><span>Model:</span> <strong>Gemini 3.5 Flash</strong></div>
    </div>
  </footer>

</body>
</html>
"""

def generate_diagram():
    output_png = "c:\\Users\\user\\Desktop\\warden_architecture_diagram.png"
    output_pdf = "c:\\Users\\user\\Desktop\\warden_architecture_diagram.pdf"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page(viewport={"width": 2560, "height": 1440}, device_scale_factor=2)
        page.set_content(HTML_CONTENT, wait_until="networkidle")
        
        # Take PNG Screenshot
        page.screenshot(path=output_png, full_page=True)
        print(f"Generated 2K Architecture PNG: {output_png}")
        
        # Generate PDF
        page.pdf(path=output_pdf, width="2560px", height="1440px", print_background=True)
        print(f"Generated Architecture PDF: {output_pdf}")
        
        browser.close()

if __name__ == "__main__":
    generate_diagram()

