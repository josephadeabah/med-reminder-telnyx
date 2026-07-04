import type { HealthSnapshot } from "@/lib/types";
import { formatDateTime } from "@/lib/format";

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="text-2xs text-muted">{label}</span>
      <span className="text-sm font-medium text-ink text-right">{value}</span>
    </div>
  );
}

export function HealthSnapshotCard({ snapshot }: { snapshot: HealthSnapshot }) {
  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <h2 className="text-2xs font-mono uppercase tracking-wide text-muted mb-2">Health snapshot</h2>
      <div className="divide-y divide-line">
        <Row
          label="30-day adherence"
          value={snapshot.adherence_30day_pct !== null ? `${snapshot.adherence_30day_pct}%` : "—"}
        />
        <Row
          label="Next appointment"
          value={
            snapshot.next_appointment_at
              ? `${formatDateTime(snapshot.next_appointment_at)}${snapshot.next_appointment_doctor ? `, ${snapshot.next_appointment_doctor}` : ""}`
              : "None scheduled"
          }
        />
        <Row
          label="Last HbA1c"
          value={
            snapshot.last_hba1c !== null
              ? `${snapshot.last_hba1c}%${snapshot.last_hba1c_at ? ` — ${new Date(snapshot.last_hba1c_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}` : ""}`
              : "—"
          }
        />
        <Row
          label={snapshot.next_refill_medication ? `${snapshot.next_refill_medication} refill` : "Next refill"}
          value={
            snapshot.next_refill_days_remaining !== null
              ? `${snapshot.next_refill_days_remaining} day${snapshot.next_refill_days_remaining === 1 ? "" : "s"} left`
              : "—"
          }
        />
      </div>
    </div>
  );
}
