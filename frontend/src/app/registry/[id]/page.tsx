"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getRegistry, getRegistryEntry } from "@/lib/api";
import { RegistryEntry } from "@/lib/types";
import { seal } from "@/lib/seal";

const pill = (s: string) => (s === "APPROVED" ? "p-att" : s === "REJECTED" ? "p-void" : "p-rev");
const word = (s: string) => (s === "APPROVED" ? "Attested" : s === "REJECTED" ? "Voided" : "Revoked");

export default function CapabilityDetail() {
  const { id } = useParams<{ id: string }>();
  const [entry, setEntry] = useState<RegistryEntry | null>(null);
  const [nf, setNf] = useState(false);
  useEffect(() => {
    (async () => {
      const all = await getRegistry();
      const e = all.find((r) => r.capability_id === id);
      if (e) { setEntry(e); return; }
      const single = await getRegistryEntry(id);
      if (single) setEntry(single); else setNf(true);
    })();
  }, [id]);
  if (nf) return <div className="page"><Link href="/registry" className="back">← Registry</Link><p>Capability not found.</p></div>;
  if (!entry) return <div className="page" style={{ color: "var(--dim)" }}>Loading…</div>;
  const ok = entry.status === "APPROVED";
  const v = entry.verdict;
  return (
    <div className="page detail">
      <Link href="/registry" className="back">← Registry</Link>
      <div className="ptitle">{entry.manifest.name}</div>
      <div className="psub mono" style={{ fontSize: ".7rem" }}>{entry.capability_id} · v{entry.version ?? 1}</div>
      <div className="detail-grid" style={{ marginTop: 10 }}>
        <div className="seal-hero">
          <span dangerouslySetInnerHTML={{ __html: seal(entry.signature || entry.capability_id, 150, ok ? "var(--seal)" : "var(--faint)") }} />
          <span className={"pill " + pill(entry.status)}>{word(entry.status)}</span>
          <div className="risk-big">{v?.risk_score ?? 0}<div className="l">Risk / 100</div></div>
        </div>
        <div>
          {v?.summary && <div className="dsec"><h3>Verdict</h3><p style={{ color: "var(--dim)" }}>{v.summary}</p></div>}
          {ok ? (
            <div className="dsec"><h3>Attestation</h3><div className="attest">
              <span dangerouslySetInnerHTML={{ __html: seal(entry.signature || entry.capability_id, 56) }} />
              <div><div className="k">Sealed by {entry.signed_by || "warden-registrar"} · ed25519</div><div className="sig">{entry.signature}…</div></div>
            </div></div>
          ) : (
            <div className="dsec"><h3>Findings — {v?.findings?.length ?? 0}</h3>
              {v?.findings?.map((f, i) => (
                <div key={i} className={"find" + (f.severity === "critical" ? " crit" : "")}>
                  <div className="fc">{f.threat_class}</div><div className="fr">{f.rationale}</div><div className="fe">{f.citation}{f.evidence ? ` · “${f.evidence}”` : ""}</div>
                </div>
              ))}
            </div>
          )}
          <div className="dsec"><h3>Manifest</h3>
            <div className="kv"><span className="k">Provider</span><span className="v">{entry.manifest.provider}</span></div>
            <div className="kv"><span className="k">Type</span><span className="v">{entry.manifest.type}</span></div>
            <div className="kv"><span className="k">Submitted by</span><span className="v"><Link href="/fleet" style={{ color: "var(--gold)" }}>{entry.manifest.submitted_by_agent}</Link></span></div>
            <div className="kv"><span className="k">Scopes</span><span className="v">{(entry.manifest.requested_scopes || []).join(", ") || "none"}</span></div>
          </div>
          {entry.provenance?.length ? (
            <div className="dsec prov"><h3>Provenance</h3>
              {entry.provenance.map((p, i) => (
                <div className="row" key={i}><span className="dot" style={{ borderColor: ok ? "var(--seal)" : "var(--threat)" }} /><div><div className="pt">{p.event}</div><div className="pd">{p.detail || p.at || ""}</div></div></div>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
