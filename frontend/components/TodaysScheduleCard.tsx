// frontend/src/components/TodaysScheduleCard.tsx
"use client";

import { useState } from "react";
import type { DoseWithCall } from "@/lib/types";
import { ApiError, triggerSystemCall } from "@/lib/api";
import { doseStatusStyle, formatTime } from "@/lib/format";
import { StatusDot } from "@/components/shared/StatusDot";

export function TodaysScheduleCard({ doses, onCallPlaced }: { doses: DoseWithCall[]; onCallPlaced: () => void }) {
  const [triggeringId, setTriggeringId] = useState<string | null>(null);

  async function handleTrigger(doseId: string) {
    setTriggeringId(doseId);
    try {
      await triggerSystemCall(doseId);
      onCallPlaced();
    } catch (err) {
      console.error(err instanceof ApiError ? err.message : err);
    } finally {
      setTriggeringId(null);
    }
  }

  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <h2 className="text-2xs font-mono uppercase tracking-wide text-muted mb-3">Today&apos;s schedule</h2>
      {doses.length === 0 ? (
        <p className="text-sm text-muted">No doses scheduled today.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {doses.map((dose) => {
            const style = doseStatusStyle(dose.status);
            const isLive = dose.call_status && ["initiated", "ringing", "answered"].includes(dose.call_status);
            return (
              <li key={dose.dose_id} className="flex items-center gap-2.5">
                <StatusDot className={isLive ? "bg-amber" : style.dot} pulsing={!!isLive} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-ink truncate">{dose.medication_name}</p>
                  <p className="text-2xs font-mono text-muted">{formatTime(dose.scheduled_for)}</p>
                </div>
                {dose.status === "pending" && !dose.call_id ? (
                  <button
                    type="button"
                    onClick={() => handleTrigger(dose.dose_id)}
                    disabled={triggeringId === dose.dose_id}
                    className="text-2xs font-mono text-accent hover:underline disabled:opacity-50"
                  >
                    {triggeringId === dose.dose_id ? "Calling…" : "Call now"}
                  </button>
                ) : (
                  <span className={`text-2xs font-medium ${isLive ? "text-amber" : style.text}`}>
                    {isLive ? "Live" : style.label}
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}