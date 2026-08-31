import os
from playwright.sync_api import sync_playwright

MINDMAP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WARDEN Mind-Map Architecture & Workflow</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #151b2b;
      --border: rgba(255, 255, 255, 0.1);
      --bone: #f8fafc;
      --dim: #94a3b8;
      --blue: #2563eb;
      --blue-border: #38bdf8;
      --purple: #7c3aed;
      --purple-border: #a855f7;
      --green: #059669;
      --green-border: #34d399;
      --gold: #d97706;
      --gold-border: #fbbf24;
      --red: #dc2626;
      --red-border: #f87171;
      --cyan: #0891b2;
      --cyan-border: #22d3ee;
      --pill-bg: #1e293b;
      --pill-border: rgba(255, 255, 255, 0.15);
      --grot: 'Space Grotesk', system-ui, sans-serif;
      --mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      width: 2560px;
      height: 1440px;
      background: var(--bg);
      color: var(--bone);
      font-family: var(--grot);
      overflow: hidden;
      padding: 40px 60px;
      position: relative;
    }

    /* TOP HEADER */
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 24px;
      border-bottom: 2px solid var(--border);
    }

    .title-group h1 {
      font-size: 2.5rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .title-group p {
      font-size: 1.15rem;
      color: var(--dim);
      margin-top: 4px;
    }

    .header-tags {
      display: flex;
      gap: 12px;
    }

    .tag-chip {
      font-family: var(--mono);
      font-size: 0.85rem;
      font-weight: 600;
      padding: 8px 16px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
    }

    /* GRAPH CANVAS */
    .graph-canvas {
      width: 100%;
      height: 1220px;
      position: relative;
      margin-top: 20px;
    }

    svg.connections {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    }

    /* NODES */
    .node {
      position: absolute;
      border-radius: 14px;
      padding: 16px 24px;
      font-weight: 600;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5);
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      transition: all 0.2s ease;
    }

    .node .node-title {
      font-size: 1.25rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .node .node-sub {
      font-family: var(--mono);
      font-size: 0.8rem;
      margin-top: 4px;
      opacity: 0.85;
    }

    /* NODE COLOR THEMES (Mermaid Style) */
    .node-blue {
      background: #1d4ed8;
      border: 2px solid var(--blue-border);
      color: #fff;
    }

    .node-green {
      background: #047857;
      border: 2px solid var(--green-border);
      color: #fff;
    }

    .node-purple {
      background: #6d28d9;
      border: 2px solid var(--purple-border);
      color: #fff;
    }

    .node-gold {
      background: #b45309;
      border: 2px solid var(--gold-border);
      color: #fff;
    }

    .node-red {
      background: #b91c1c;
      border: 2px solid var(--red-border);
      color: #fff;
    }

    .node-cyan {
      background: #0e7490;
      border: 2px solid var(--cyan-border);
      color: #fff;
    }

    .node-dark {
      background: #1e293b;
      border: 2px solid #64748b;
      color: #fff;
    }

    /* LABELED CONNECTOR PILLS */
    .pill {
      position: absolute;
      z-index: 3;
      background: var(--pill-bg);
      border: 1px solid var(--pill-border);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      color: #e2e8f0;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      transform: translate(-50%, -50%);
      white-space: nowrap;
    }

    .pill strong {
      color: #38bdf8;
    }

    .pill.threat-pill {
      border-color: rgba(248, 113, 113, 0.4);
      background: #2b1418;
    }
    .pill.threat-pill strong { color: #f87171; }

    .pill.seal-pill {
      border-color: rgba(52, 211, 153, 0.4);
      background: #0d281e;
    }
    .pill.seal-pill strong { color: #34d399; }
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="header-bar">
    <div class="title-group">
      <h1>🛡️ WARDEN: Multi-Agent System Architecture & Workflow</h1>
      <p>Decoupled Separation-of-Duties Mind Map across Autonomous Ingress, Inspection, Cryptographic Minting & Runtime Gating</p>
    </div>
    <div class="header-tags">
      <div class="tag-chip" style="color: #c084fc; border-color: #a855f7;">Google ADK Pipeline</div>
      <div class="tag-chip" style="color: #6ee7b7; border-color: #34d399;">Ed25519 Wax Seals</div>
      <div class="tag-chip" style="color: #7dd3fc; border-color: #38bdf8;">Cloud Run & Vertex AI</div>
    </div>
  </div>

  <!-- GRAPH CANVAS -->
  <div class="graph-canvas">

    <!-- SVG ARROWS & CONNECTORS -->
    <svg class="connections">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#94a3b8" />
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#f87171" />
        </marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8" />
        </marker>
        <marker id="arrow-gold" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#fbbf24" />
        </marker>
      </defs>

      <!-- Client to Inspector -->
      <path d="M 1220 110 C 900 110, 680 180, 560 250" fill="none" stroke="#94a3b8" stroke-width="3" marker-end="url(#arrow)" />

      <!-- Inspector to Vertex AI (Reasoning) -->
      <path d="M 400 310 C 260 310, 200 420, 200 520" fill="none" stroke="#a855f7" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)" />
      
      <!-- Inspector to Threat Block -->
      <path d="M 480 340 C 420 440, 420 540, 420 640" fill="none" stroke="#f87171" stroke-width="3" marker-end="url(#arrow-red)" />

      <!-- Inspector to Registrar -->
      <path d="M 680 310 C 860 310, 880 430, 880 520" fill="none" stroke="#34d399" stroke-width="3.5" marker-end="url(#arrow-green)" />

      <!-- Registrar to Secret Manager -->
      <path d="M 760 580 C 640 580, 600 700, 600 800" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow-gold)" />

      <!-- Registrar to Firestore Registry -->
      <path d="M 980 580 C 1120 580, 1160 700, 1180 800" fill="none" stroke="#34d399" stroke-width="3.5" marker-end="url(#arrow-green)" />

      <!-- Client to Gatekeeper (Runtime Invocation) -->
      <path d="M 1340 110 C 1660 110, 1860 180, 1920 250" fill="none" stroke="#38bdf8" stroke-width="3.5" marker-end="url(#arrow-blue)" />

      <!-- Gatekeeper to Firestore Registry (Signature Check) -->
      <path d="M 1840 310 C 1600 380, 1340 600, 1260 800" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)" />

      <!-- Gatekeeper to Model Armor (Payload Screen) -->
      <path d="M 2040 310 C 2200 400, 2260 520, 2260 640" fill="none" stroke="#22d3ee" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)" />

      <!-- Gatekeeper to Target Tool Execution -->
      <path d="M 1940 340 C 1940 480, 1940 660, 1940 800" fill="none" stroke="#34d399" stroke-width="3.5" marker-end="url(#arrow-green)" />

      <!-- Gatekeeper to Cloud Trace Telemetry -->
      <path d="M 2060 330 C 2300 460, 2380 660, 2380 800" fill="none" stroke="#a855f7" stroke-width="3" marker-end="url(#arrow)" />

      <!-- Sweeper loop: Cloud Scheduler -> Sweeper Daemon -> Inspector -> Auto-Revoke Firestore -->
      <path d="M 1520 860 C 1580 980, 1540 1080, 1420 1100" fill="none" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrow-gold)" />
      <path d="M 1260 1100 C 1020 1100, 940 1020, 1140 870" fill="none" stroke="#f87171" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow-red)" />
    </svg>

    <!-- ==================== NODES ==================== -->

    <!-- Top Center Root Node: Client & Autonomous Agents -->
    <div class="node node-blue" style="top: 40px; left: 1040px; width: 480px; height: 110px;">
      <div class="node-title">🤖 Autonomous Agent Fleet / MCP Client</div>
      <div class="node-sub">Ingress Layer · Perimeter UI Dashboard · Studio Batch Uploads</div>
    </div>

    <!-- Agent 1: The Inspector -->
    <div class="node node-purple" style="top: 250px; left: 420px; width: 380px; height: 110px;">
      <div class="node-title">🔍 1. The Inspector Agent</div>
      <div class="node-sub">Gemini 3.5 Flash · Static OWASP Analysis & Scopes</div>
    </div>

    <!-- Vertex AI Reasoning Node -->
    <div class="node node-dark" style="top: 520px; left: 60px; width: 300px; height: 95px;">
      <div class="node-title">🧠 Vertex AI API</div>
      <div class="node-sub">gemini-3.5-flash · Grounded Findings</div>
    </div>

    <!-- Threat / Rejected Block Node -->
    <div class="node node-red" style="top: 640px; left: 320px; width: 300px; height: 95px;">
      <div class="node-title">🛑 Malicious Tool Blocked</div>
      <div class="node-sub">OWASP LLM01 / Exfil Grounded Evidence</div>
    </div>

    <!-- Agent 2: The Registrar -->
    <div class="node node-green" style="top: 520px; left: 740px; width: 360px; height: 110px;">
      <div class="node-title">🔏 2. The Registrar Agent</div>
      <div class="node-sub">Ed25519 Cryptographic Minting & Monotonic Versions</div>
    </div>

    <!-- Secret Manager Node -->
    <div class="node node-gold" style="top: 800px; left: 480px; width: 290px; height: 95px;">
      <div class="node-title">🔐 Secret Manager</div>
      <div class="node-sub">Hardware Ed25519 Private Key</div>
    </div>

    <!-- Firestore Registry Node (Center Database Hub) -->
    <div class="node node-green" style="top: 800px; left: 1040px; width: 440px; height: 120px; box-shadow: 0 0 40px rgba(52, 211, 153, 0.2);">
      <div class="node-title">🗄️ Firestore Capability Registry</div>
      <div class="node-sub">Signed Provenance Catalog (`warden_registry`) & Audit Docket</div>
    </div>

    <!-- Agent 3: The Gatekeeper -->
    <div class="node node-blue" style="top: 250px; left: 1760px; width: 380px; height: 110px;">
      <div class="node-title">🛡️ 3. The Gatekeeper Agent</div>
      <div class="node-sub">Runtime Zero-Trust Interception & Policy Enforcement</div>
    </div>

    <!-- Model Armor Node -->
    <div class="node node-cyan" style="top: 640px; left: 2120px; width: 280px; height: 95px;">
      <div class="node-title">🛡️ Model Armor</div>
      <div class="node-sub">Inline Jailbreak & PII Screen</div>
    </div>

    <!-- Approved Target Execution Node -->
    <div class="node node-green" style="top: 800px; left: 1780px; width: 340px; height: 95px;">
      <div class="node-title">⚡ Approved Tool Execution</div>
      <div class="node-sub">Forwarded to Safe MCP Server / API</div>
    </div>

    <!-- Cloud Trace Node -->
    <div class="node node-purple" style="top: 800px; left: 2220px; width: 280px; height: 95px;">
      <div class="node-title">📊 Google Cloud Trace</div>
      <div class="node-sub">OpenTelemetry Distributed Spans</div>
    </div>

    <!-- Sweeper / Background Loop Node -->
    <div class="node node-gold" style="top: 1050px; left: 1240px; width: 400px; height: 105px;">
      <div class="node-title">⏰ Sweeper Daemon & Pub/Sub</div>
      <div class="node-sub">Continuous Background Re-Auditing & Auto-Revocation</div>
    </div>

    <!-- ==================== LABELED CONNECTOR PILLS ==================== -->
    <div class="pill" style="top: 170px; left: 860px;"><strong>1. Submit Tool Manifest</strong> (JSON Schema)</div>
    <div class="pill" style="top: 400px; left: 210px;">Structured LLM Reasoning</div>
    <div class="pill threat-pill" style="top: 490px; left: 440px;"><strong>Risk Score &ge; 70</strong> (Reject & Log)</div>
    <div class="pill seal-pill" style="top: 390px; left: 860px;"><strong>2. VettingVerdict: Clean</strong> (Risk &lt; 20)</div>
    <div class="pill" style="top: 710px; left: 630px;">Load Private Key (Ed25519)</div>
    <div class="pill seal-pill" style="top: 710px; left: 1060px;"><strong>3. Store Signed Wax-Seal Entry</strong></div>

    <div class="pill" style="top: 170px; left: 1680px;"><strong>4. Runtime Tool Invocation</strong> (Agent Tool Call)</div>
    <div class="pill" style="top: 520px; left: 1540px;">5. Verify Signature & Agent Scopes</div>
    <div class="pill" style="top: 480px; left: 2190px;">6. Inline Guardrail Filter</div>
    <div class="pill seal-pill" style="top: 580px; left: 1940px;"><strong>7. Verified (ALLOW)</strong></div>
    <div class="pill" style="top: 560px; left: 2360px;">8. Emit Audit Spans</div>

    <div class="pill" style="top: 980px; left: 1560px;">Cloud Scheduler Trigger</div>
    <div class="pill threat-pill" style="top: 1010px; left: 1050px;">Auto-Revoke Compromised Tools</div>

  </div>

</body>
</html>
"""

def generate_mindmap():
    output_png = "c:\\Users\\user\\Desktop\\warden_architecture_diagram.png"
    output_pdf = "c:\\Users\\user\\Desktop\\warden_architecture_diagram.pdf"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page(viewport={"width": 2560, "height": 1440}, device_scale_factor=2)
        page.set_content(MINDMAP_HTML, wait_until="networkidle")
        
        # Take PNG Screenshot
        page.screenshot(path=output_png, full_page=True)
        print(f"Generated Mind-Map Architecture PNG: {output_png}")
        
        # Generate PDF
        page.pdf(path=output_pdf, width="2560px", height="1440px", print_background=True)
        print(f"Generated Mind-Map Architecture PDF: {output_pdf}")
        
        browser.close()

if __name__ == "__main__":
    generate_mindmap()
