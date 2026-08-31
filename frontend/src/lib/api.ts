import { RegistryEntry, AuditEvent, CapabilityManifest } from "./types";

const BASE = process.env.NEXT_PUBLIC_WARDEN_API || "";

async function req<T>(path: string, init?: RequestInit, timeoutMs?: number): Promise<T | null> {
  if (!BASE) return null;
  // Optional timeout so a slow/hung backend never freezes the UI.
  const ctrl = timeoutMs ? new AbortController() : null;
  const timer = ctrl ? setTimeout(() => ctrl.abort(), timeoutMs) : null;
  try {
    const r = await fetch(BASE + path, { cache: "no-store", ...(ctrl ? { signal: ctrl.signal } : {}), ...init });
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

/* LIVE DATA ONLY — no seeded or demo history is ever injected. An empty backend
   shows an empty state; real decisions appear as they happen. */

export async function getRegistry(): Promise<RegistryEntry[]> {
  const d = await req<RegistryEntry[]>("/registry", undefined, 8000);
  const list = Array.isArray(d) ? d : [];
  const m = new Map<string, RegistryEntry>();
  list.forEach((r) => { const p = m.get(r.capability_id); if (!p || (r.version ?? 0) >= (p.version ?? 0)) m.set(r.capability_id, r); });
  return [...m.values()];
}

export async function getRegistryEntry(id: string): Promise<RegistryEntry | null> {
  const d = await req<RegistryEntry>(`/registry/${encodeURIComponent(id)}`, undefined, 8000);
  if (!d || (d as unknown as { error?: string }).error || !d.capability_id) return null;
  return d;
}

export async function getAudit(): Promise<AuditEvent[]> {
  const d = await req<AuditEvent[]>("/audit?limit=60", undefined, 8000);
  return Array.isArray(d) ? d : [];
}

export async function vetCapability(manifest: CapabilityManifest): Promise<RegistryEntry | null> {
  // 45s bound: generous for the live Gemini Inspector, but never hangs forever.
  return req<RegistryEntry>("/capabilities", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(manifest),
  }, 45000);
}


const VALID_TYPES = ["tool", "mcp_server", "model", "api"];

// Fill in every field the WARDEN backend requires, so ANY manifest a judge pastes
// or uploads validates (the deployed API requires provider/version/etc.). Only
// name/description really matter from the submitter; the rest get sane defaults.
// raw_definition falls back to the exact text/JSON submitted, so the Gemini
// Inspector analyses precisely what was provided.
export function normalizeManifest(input: unknown, rawText?: string): CapabilityManifest {
  const m = (input && typeof input === "object" ? input : {}) as Record<string, any>;
  const name = String(m.name || m.capability_id || "unnamed-capability");
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "capability";
  const type = VALID_TYPES.includes(m.type) ? m.type : "tool";
  return {
    capability_id: String(m.capability_id || m.id || `cap-${slug}`),
    name,
    type,
    description: String(m.description || ""),
    provider: String(m.provider || "user-submitted"),
    version: String(m.version || "1.0.0"),
    endpoint: m.endpoint,
    input_schema: m.input_schema,
    output_schema: m.output_schema,
    requested_scopes: Array.isArray(m.requested_scopes) ? m.requested_scopes : [],
    raw_definition: String(m.raw_definition || rawText || JSON.stringify(m)),
    submitted_by_agent: String(m.submitted_by_agent || "external-submitter"),
    submitted_at: String(m.submitted_at || new Date().toISOString()),
  };
}
