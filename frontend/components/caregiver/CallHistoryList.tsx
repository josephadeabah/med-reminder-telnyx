import type { CallSummary } from "@/lib/types";
import { callReasonLabel, callStatusStyle, formatRelative } from "@/lib/format";
import { StatusDot } from "@/components/shared/StatusDot";

export function CallHistoryList({ title, calls, emptyText }: { title: string; calls: CallSummary[]; emptyText: string }) {
  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <h2 className="text-2xs font-mono uppercase tracking-wide text-muted mb-3">{title}</h2>
      {calls.length === 0 ? (
        <p className="text-sm text-muted">{emptyText}</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {calls.map((call) => {
            const style = callStatusStyle(call.status);
            const detail =
              call.direction === "system"
                ? call.intent === "taken"
                  ? "Confirmed"
                  : call.intent === "not_taken"
                    ? "Not taken"
                    : style.label
                : callReasonLabel(call.call_reason);
            return (
              <li key={call.id} className="flex items-center gap-2.5">
                <StatusDot className={style.dot} pulsing={style.pulsing} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-ink truncate">
                    {call.medication_name ? `${call.medication_name} check` : detail}
                  </p>
                  <p className="text-2xs font-mono text-muted">{formatRelative(call.created_at)}</p>
                </div>
                <span className={`text-2xs font-medium ${style.text}`}>
                  {call.direction === "system" ? detail : style.label}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
