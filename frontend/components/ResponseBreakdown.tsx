// frontend/src/components/ResponseBreakdown.tsx
import type { ResponseBreakdown as ResponseBreakdownType } from "@/lib/types";

const SEGMENTS: { key: keyof ResponseBreakdownType; label: string; barClass: string; textClass: string }[] = [
  { key: "confirmed_taken_pct", label: "Confirmed taken", barClass: "bg-accent", textClass: "text-accent" },
  { key: "not_taken_pct", label: "Reported not taken", barClass: "bg-clay", textClass: "text-clay" },
  { key: "no_answer_pct", label: "No answer", barClass: "bg-amber", textClass: "text-amber" },
  { key: "skipped_pct", label: "Skipped / unclear", barClass: "bg-muted", textClass: "text-muted" },
];

export function ResponseBreakdown({ breakdown, periodDays }: { breakdown: ResponseBreakdownType; periodDays: number }) {
  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <h2 className="text-2xs font-mono uppercase tracking-wide text-muted mb-1">Response breakdown</h2>
      <p className="text-2xs font-mono text-muted mb-4">Based on resolved calls — last {periodDays} days</p>

      <div className="w-full h-2.5 rounded-full overflow-hidden bg-paper flex mb-4">
        {SEGMENTS.map((seg) => (
          <div key={seg.key} className={seg.barClass} style={{ width: `${breakdown[seg.key]}%` }} />
        ))}
      </div>

      <ul className="flex flex-col gap-2">
        {SEGMENTS.map((seg) => (
          <li key={seg.key} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-ink">
              <span className={`h-2 w-2 rounded-full ${seg.barClass}`} />
              {seg.label}
            </span>
            <span className={`font-mono text-2xs font-medium ${seg.textClass}`}>{breakdown[seg.key]}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}