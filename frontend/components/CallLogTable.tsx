// components/CallLogTable.tsx
import type { CallSummary } from "@/lib/types";
import { callStatusStyle, formatDateTime, escalationLevelLabel } from "@/lib/format";
import { StatusDot } from "@/components/shared/StatusDot";

function durationLabel(createdAt: string, updatedAt: string): string {
  const seconds = Math.max(
    0,
    Math.round((new Date(updatedAt).getTime() - new Date(createdAt).getTime()) / 1000)
  );
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function responseLabel(call: CallSummary): string {
  if (call.intent === "taken") return '✅ "Yes, took it"';
  if (call.intent === "not_taken") return '❌ "No, not yet"';
  if (call.intent === "emergency") return "🚨 Emergency alert";
  if (call.status === "no-answer" || call.status === "busy") return "No answer";
  return "⏳ Awaiting response…";
}

function directionLabel(call: CallSummary): string {
  if (call.direction === "system_to_patient") return "📞 To patient";
  if (call.direction === "system_to_caregiver") return "🚨 To caregiver";
  return call.direction;
}

export function CallLogTable({ calls }: { calls: CallSummary[] }) {
  return (
    <div className="rounded-xl border border-line bg-surface overflow-hidden">
      <div className="px-5 py-3 border-b border-line">
        <h2 className="text-2xs font-mono uppercase tracking-wide text-muted">Call log</h2>
      </div>
      {calls.length === 0 ? (
        <div className="px-5 py-12 text-center text-sm text-muted">No calls yet.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-2xs font-mono uppercase tracking-wide text-muted text-left">
                <th className="px-5 py-2 font-medium">Date &amp; time</th>
                <th className="px-5 py-2 font-medium">Direction</th>
                <th className="px-5 py-2 font-medium">Medication</th>
                <th className="px-5 py-2 font-medium">Status</th>
                <th className="px-5 py-2 font-medium">Escalation</th>
                <th className="px-5 py-2 font-medium">Response</th>
                <th className="px-5 py-2 font-medium">Duration</th>
              </tr>
            </thead>
            <tbody>
              {calls.map((call) => {
                const style = callStatusStyle(call.status);
                return (
                  <tr key={call.call_id} className="border-t border-line">
                    <td className="px-5 py-3 font-mono text-2xs text-muted whitespace-nowrap">
                      {formatDateTime(call.created_at)}
                    </td>
                    <td className="px-5 py-3 text-2xs font-mono text-muted whitespace-nowrap">
                      {directionLabel(call)}
                    </td>
                    <td className="px-5 py-3 text-ink whitespace-nowrap">
                      {call.medication_name ?? "—"}
                    </td>
                    <td className="px-5 py-3">
                      <span className="inline-flex items-center gap-1.5">
                        <StatusDot className={style.dot} pulsing={style.pulsing} />
                        <span className={`text-2xs font-medium ${style.text}`}>
                          {style.label}
                        </span>
                      </span>
                    </td>
                    <td className="px-5 py-3 text-2xs font-mono text-muted">
                      {call.escalation_level ? escalationLevelLabel(call.escalation_level) : "—"}
                    </td>
                    <td className="px-5 py-3 text-muted">{responseLabel(call)}</td>
                    <td className="px-5 py-3 font-mono text-2xs text-muted">
                      {durationLabel(call.created_at, call.updated_at)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}