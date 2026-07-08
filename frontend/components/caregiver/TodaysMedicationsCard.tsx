import type { DoseWithCall } from "@/lib/types";
import { doseStatusStyle, formatTime } from "@/lib/format";
import { StatusDot } from "@/components/shared/StatusDot";

export function TodaysMedicationsCard({ doses }: { doses: DoseWithCall[] }) {
  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <h2 className="text-2xs font-mono uppercase tracking-wide text-muted mb-3">Today&apos;s medications</h2>
      {doses.length === 0 ? (
        <p className="text-sm text-muted">No doses scheduled today.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {doses.map((dose) => {
            const style = doseStatusStyle(dose.status);
            return (
              <li key={dose.dose_id} className="flex items-center gap-2.5">
                <StatusDot className={style.dot} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-ink truncate">
                    {dose.medication_name} {dose.medication_dose_text}
                  </p>
                  <p className="text-2xs font-mono text-muted">{formatTime(dose.scheduled_for)}</p>
                </div>
                <span className={`text-2xs font-medium ${style.text}`}>{style.label}</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}