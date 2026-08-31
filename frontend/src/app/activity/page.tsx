"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAudit } from "@/lib/api";
import { AuditEvent } from "@/lib/types";

export default function Activity() {
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const router = useRouter();
  useEffect(() => {
    const load = () => getAudit().then(setAudit);
    load();
    const iv = setInterval(load, 8000); // live refresh
    return () => clearInterval(iv);
  }, []);
  const rows = audit.filter((e, i) => i === 0 || !(audit[i - 1].capability_id === e.capability_id && audit[i - 1].reason === e.reason));
  return (
    <div className="page">
      <div className="ptitle">Activity</div>
      <div className="psub">Gateway decisions · click a row to inspect the capability</div>
      {rows.length === 0 ? (
        <div className="vempty">No gateway activity yet &mdash; fire a capability at the Perimeter to see live decisions here.</div>
      ) : (
      <div className="table">
        <div className="trow hd"><span>Timestamp</span><span>Decision</span><span>Detail</span><span /></div>
        {rows.map((e, i) => (
          <div key={i} className={"trow" + (e.capability_id ? " link" : "") + (e.decision === "BLOCK" ? " row-block" : " row-allow")} onClick={() => e.capability_id && router.push(`/registry/${e.capability_id}`)}>
            <span className="tt">{(e.timestamp || "").replace("T", " ").replace(/\..*/, "")}</span>
            <span className={"pill " + (e.decision === "BLOCK" ? "p-void" : "p-att")}>{e.decision === "BLOCK" ? "Block" : "Allow"}</span>
            <span className="msg"><b>{e.capability_id}</b> — {e.reason}</span>
            <span className="arr">›</span>
          </div>
        ))}
      </div>
      )}
    </div>
  );
}
