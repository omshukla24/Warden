export interface Finding {
  threat_class: string;
  severity?: string;
  evidence?: string;
  location?: string;
  rationale?: string;
  citation?: string;
}
export interface VettingVerdict {
  capability_id?: string;
  decision: "APPROVE" | "BLOCK" | "QUARANTINE";
  risk_score: number;
  threat_classes?: string[];
  findings?: Finding[];
  summary?: string;
  model_used?: string;
}
export interface CapabilityManifest {
  capability_id: string;
  name: string;
  type?: string;
  description?: string;
  provider?: string;
  version?: string;
  endpoint?: string;
  input_schema?: unknown;
  output_schema?: unknown;
  requested_scopes?: string[];
  raw_definition?: string;
  submitted_by_agent?: string;
  submitted_at?: string;
}
export interface RegistryEntry {
  capability_id: string;
  manifest: CapabilityManifest;
  verdict?: VettingVerdict;
  status: "APPROVED" | "REJECTED" | "REVOKED";
  signature?: string | null;
  signed_by?: string | null;
  provenance?: { event: string; at?: string; detail?: string }[];
  version?: number;
}
export interface AuditEvent {
  event_id?: string;
  event_type?: string;
  capability_id?: string;
  invoking_agent?: string | null;
  decision?: "ALLOW" | "BLOCK";
  reason?: string;
  timestamp?: string;
}
