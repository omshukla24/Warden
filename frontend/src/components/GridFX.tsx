"use client";
import { useEffect, useRef } from "react";

// Lightweight twinkling-dot layer. The static square grid comes from CSS
// (body::after); this canvas only lights up a few grid points at a time, so it
// stays cheap (~18fps, a couple dozen small arcs per frame).
export default function GridFX() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const reduce = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const GAP = 46; // matches the CSS grid in body::after
    const COLORS = ["79,219,160", "255,230,166", "255,77,84", "154,124,255", "110,168,255"];
    let w = 0, h = 0;
    const dpr = Math.min(typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1, 2);
    const resize = () => {
      w = window.innerWidth; h = window.innerHeight;
      canvas.width = Math.floor(w * dpr); canvas.height = Math.floor(h * dpr);
      canvas.style.width = w + "px"; canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    type Twinkle = { x: number; y: number; t0: number; dur: number; c: string };
    let twinkles: Twinkle[] = [];
    let raf = 0, last = 0;

    const draw = (now: number) => {
      raf = requestAnimationFrame(draw);
      if (now - last < 55) return; // ~18fps cap
      last = now;
      ctx.clearRect(0, 0, w, h);
      if (!reduce && twinkles.length < 28 && Math.random() < 0.6) {
        const cols = Math.floor(w / GAP), rows = Math.floor(h / GAP);
        twinkles.push({
          x: Math.floor(Math.random() * cols) * GAP,
          y: Math.floor(Math.random() * rows) * GAP,
          t0: now,
          dur: 1000 + Math.random() * 1800,
          c: COLORS[Math.floor(Math.random() * COLORS.length)],
        });
      }
      twinkles = twinkles.filter((t) => now - t.t0 < t.dur);
      for (const t of twinkles) {
        const p = (now - t.t0) / t.dur;
        const a = Math.sin(p * Math.PI) * 0.85; // fade in then out
        if (a <= 0) continue;
        ctx.beginPath();
        ctx.fillStyle = `rgba(${t.c},${a.toFixed(3)})`;
        ctx.shadowColor = `rgba(${t.c},${(a * 0.9).toFixed(3)})`;
        ctx.shadowBlur = 7;
        ctx.arc(t.x, t.y, 1.7, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    };
    raf = requestAnimationFrame(draw);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); };
  }, []);
  return <canvas ref={ref} className="gridfx" aria-hidden="true" />;
}
