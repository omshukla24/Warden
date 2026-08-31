"use client";
import { useCallback, useEffect, useState } from "react";
import Perimeter from "@/components/Perimeter";
import { getRegistry, getAudit } from "@/lib/api";
import { RegistryEntry, AuditEvent } from "@/lib/types";

export default function Home() {
  const [reg, setReg] = useState<RegistryEntry[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [ready, setReady] = useState(false);
  const load = useCallback(async () => {
    const [r, a] = await Promise.all([getRegistry(), getAudit()]);
    setReg(r); setAudit(a); setReady(true);
  }, []);
  useEffect(() => { load(); const iv = setInterval(load, 12000); return () => clearInterval(iv); }, [load]);
  if (!ready) return <div style={{ padding: 40, color: "var(--dim)", fontFamily: "var(--mono)" }}>Initializing perimeter…</div>;
  return <Perimeter registry={reg} audit={audit} onRefresh={load} />;
}
