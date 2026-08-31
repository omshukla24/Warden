// Procedural wax-seal SVG generated deterministically from a signature/id.
function hb(str: string): number[] {
  const o: number[] = []; let h = 2166136261 >>> 0; const s = str || "x";
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; o.push((h >>> ((i % 4) * 8)) & 255); }
  while (o.length < 48) { h = Math.imul(h ^ o.length, 16777619) >>> 0; o.push(h & 255); }
  return o;
}
export function seal(seed: string, size: number, color = "var(--seal)"): string {
  const b = hb(seed), c = size / 2, R = size / 2 - 2, col = color;
  let s = `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" style="filter:drop-shadow(0 0 4px rgba(79,219,160,.5))">`;
  s += `<circle cx="${c}" cy="${c}" r="${R}" fill="none" stroke="${col}" stroke-width="1" opacity=".85"/>`;
  s += `<circle cx="${c}" cy="${c}" r="${R - 4}" fill="none" stroke="${col}" stroke-width=".5" opacity=".4"/>`;
  const T = 48;
  for (let i = 0; i < T; i++) { if (!((b[i % b.length] >> (i % 8)) & 1)) continue; const a = (i / T) * Math.PI * 2;
    s += `<line x1="${(c + Math.cos(a) * (R - 1)).toFixed(1)}" y1="${(c + Math.sin(a) * (R - 1)).toFixed(1)}" x2="${(c + Math.cos(a) * (R - 4.5)).toFixed(1)}" y2="${(c + Math.sin(a) * (R - 4.5)).toFixed(1)}" stroke="${col}" stroke-width=".7" opacity=".7"/>`; }
  const k = 4 + (b[3] % 4), rr = R - 9;
  for (let f = 0; f < k; f++) { const base = (f / k) * Math.PI * 2; let d = `M ${c} ${c}`;
    for (let j = 0; j < 4; j++) { const ang = base + (b[(f + j) % b.length] / 255) * (Math.PI / k) * 1.8, rad = rr * (0.35 + (b[(f * 2 + j) % b.length] / 255) * 0.6);
      d += ` L ${(c + Math.cos(ang) * rad).toFixed(1)} ${(c + Math.sin(ang) * rad).toFixed(1)}`; }
    s += `<path d="${d}" fill="none" stroke="${col}" stroke-width=".7" opacity=".8"/>`; }
  s += `<circle cx="${c}" cy="${c}" r="${2 + (b[7] % 3)}" fill="${col}"/></svg>`;
  return s;
}
