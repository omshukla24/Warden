"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getRegistry } from "@/lib/api";
import { RegistryEntry } from "@/lib/types";

export default function Fleet() {
  const [reg, setReg] = useState<RegistryEntry[]>([]);
  useEffect(() => { getRegistry().then(setReg); }, []);
  const agents: Record<string, RegistryEntry[]> = {};
  reg.forEach((r) => { const a = r.manifest.submitted_by_agent || "unassigned"; (agents[a] ||= []).push(r); });
  return (
    <div className="page">
      <div className="ptitle">Fleet</div>
      <div className="psub">Each agent and every capability it has submitted to WARDEN — a green dot means sealed (approved), red means blocked/voided. Click any capability to inspect its verdict.</div>
      {Object.keys(agents).length === 0 && <div className="vempty">No agents yet &mdash; fire capabilities at the Perimeter to populate the fleet.</div>}
      {Object.entries(agents).map(([name, caps]) => (
        <div className="agent" key={name}>
          <div className="ah">
            <div className="av">{name[0].toUpperCase()}</div>
            <div><div className="an">{name}</div><div className="ad">{caps.length} capabilities · {caps.filter((c) => c.status === "APPROVED").length} sealed</div></div>
          </div>
          <div className="caps">
            {caps.map((c) => (
              <Link key={c.capability_id} href={`/registry/${c.capability_id}`} className="capchip">
                <span className="pill" style={{ padding: 0, background: "none" }}>
                  <span style={{ width: 6, height: 6, borderRadius: 99, background: c.status === "APPROVED" ? "var(--seal)" : c.status === "REJECTED" ? "var(--threat)" : "var(--gold-soft)", display: "inline-block" }} />
                </span>
                {c.manifest.name}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
