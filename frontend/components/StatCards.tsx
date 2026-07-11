// frontend/src/components/StatCards.tsx
import type { DashboardStats } from "@/lib/types";

function Card({ label, value, sub, tone }: { label: string; value: string; sub?: string; tone?: "accent" | "clay" }) {
  const valueClass = tone === "clay" ? "text-clay" : tone === "accent" ? "text-accent" : "text-ink";
  return (
    <div className="rounded-xl border border-line bg-surface p-4">
      <p className="text-2xs font-mono uppercase tracking-wide text-muted">{label}</p>
      <p className={`text-2xl font-semibold mt-1 ${valueClass}`}>{value}</p>
      {sub && <p className="text-2xs font-mono text-muted mt-0.5">{sub}</p>}
    </div>
  );
}

export function StatCards({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <Card label="Confirmed doses" value={`${stats.confirmed_pct}%`} sub={`Last ${stats.period_days} days`} tone="accent" />
      <Card
        label="Missed / no answer"
        value={String(stats.missed_or_no_answer_count)}
        sub={`Last ${stats.period_days} days`}
        tone={stats.missed_or_no_answer_count > 0 ? "clay" : undefined}
      />
      <Card
        label="Upcoming appointments"
        value={String(stats.upcoming_appointments_count)}
        sub={stats.next_appointment_doctor ? `Next: ${stats.next_appointment_doctor}` : undefined}
      />
    </div>
  );
}