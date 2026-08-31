"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/", label: "Perimeter" },
  { href: "/registry", label: "Registry" },
  { href: "/vetting", label: "Vetting" },
  { href: "/fleet", label: "Fleet" },
  { href: "/activity", label: "Activity" },
];
export default function Nav() {
  const path = usePathname();
  return (
    <nav className="nav">
      <div className="brand"><h1>WARDEN</h1><span className="s">Registry</span></div>
      {items.map((it) => {
        const on = it.href === "/" ? path === "/" : path.startsWith(it.href);
        return (
          <Link key={it.href} href={it.href} className={on ? "on" : ""}>
            <span className="dot" />{it.label}
          </Link>
        );
      })}
      <div className="foot">
        <div className="live"><span className="d" />Live on Cloud Run</div>
        <div className="url">warden-api…run.app</div>
      </div>
    </nav>
  );
}
