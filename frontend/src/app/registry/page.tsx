"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getRegistry } from "@/lib/api";
import { RegistryEntry } from "@/lib/types";
import { seal } from "@/lib/seal";

const pill = (s: string) => (s === "APPROVED" ? "p-att" : s === "REJECTED" ? "p-void" : "p-rev");
const word = (s: string) => (s === "APPROVED" ? "Attested" : s === "REJECTED" ? "Voided" : "Revoked");
const rc = (r: number) => (r >= 66 ? "var(--threat)" : r >= 33 ? "var(--gold-soft)" : "var(--seal)");

export default function Registry() {
  const [all, setAll] = useState<RegistryEntry[]>([]);
  const [f, setF] = useState("all");
  const [q, setQ] = useState("");
  useEffect(() => { getRegistry().then(setAll); }, []);
  const list = all.filter((r) => (f === "all" || r.status === f) && (r.manifest.name + (r.manifest.provider || "")).toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="page">
      <div className="ptitle">Registry</div>
      <div className="psub">Every capability on record · click any to inspect</div>
      <div className="search"><input placeholder="Search capabilities…" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      <div className="chips">
        {[["all", "All"], ["APPROVED", "Attested"], ["REJECTED", "Voided"], ["REVOKED", "Revoked"]].map(([k, l]) => (
          <button key={k} className={"chip" + (f === k ? " on" : "")} onClick={() => setF(k)}>{l}</button>
        ))}
      </div>
      {list.length === 0 ? (
        <div className="vempty">{all.length === 0 ? "No capabilities on record yet \u2014 fire one at the Perimeter or submit a manifest in Vetting." : "No capabilities match your search."}</div>
      ) : (
      <div className="grid">
        {list.map((r) => {
          const risk = r.verdict?.risk_score ?? 0;
          return (
            <Link key={r.capability_id} href={`/registry/${r.capability_id}`} className="card">
              <div className="top">
                <span dangerouslySetInnerHTML={{ __html: seal(r.signature || r.capability_id, 48, r.status === "APPROVED" ? "var(--seal)" : "var(--faint)") }} />
                <div style={{ flex: 1 }}><div className="nm">{r.manifest.name}</div><div className="pv">{r.manifest.provider}</div></div>
                <span className={"pill " + pill(r.status)}>{word(r.status)}</span>
              </div>
              <div className="risk"><div className="rl"><span>RISK</span><span>{risk} / 100</span></div><div className="rbar"><i style={{ width: Math.max(4, risk) + "%", background: rc(risk) }} /></div></div>
            </Link>
          );
        })}
      </div>
      )}
    </div>
  );
}
