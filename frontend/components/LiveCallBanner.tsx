"use client";

import { useState } from "react";
import type { CallSummary } from "@/lib/types";
import { ApiError, endCall } from "@/lib/api";
import { formatRelative } from "@/lib/format";
import { StatusDot } from "@/components/shared/StatusDot";

export function LiveCallBanner({ call, onEnded }: { call: CallSummary; onEnded: () => void }) {
  const [ending, setEnding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleEnd() {
    setEnding(true);
    setError(null);
    try {
      await endCall(call.call_id);
      onEnded();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't end the call.");
    } finally {
      setEnding(false);
    }
  }

  const isPatientCall = call.direction === "system_to_patient";
  const isCaregiverAlert = call.direction === "system_to_caregiver";

  return (
    <div className="rounded-xl bg-accent text-white p-5 flex items-center justify-between gap-4 flex-wrap">
      <div className="flex items-center gap-3">
        <StatusDot className="bg-white" pulsing />
        <div>
          <p className="text-2xs font-mono uppercase tracking-wide text-white/70">
            {isPatientCall && "📞 Live AI call to patient"}
            {isCaregiverAlert && "🚨 Emergency call to caregiver"}
            {!isPatientCall && !isCaregiverAlert && "Live call in progress"}
          </p>
          <p className="text-sm font-medium mt-0.5">
            {call.medication_name ? `${call.medication_name} check` : "Call"} — {call.patient_name}
          </p>
          <p className="text-2xs font-mono text-white/70 mt-0.5">
            Started {formatRelative(call.created_at)} · {call.status}
            {call.escalation_level && ` · ${call.escalation_level}`}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {error && <span className="text-2xs font-mono text-white/90">{error}</span>}
        <button
          type="button"
          onClick={handleEnd}
          disabled={ending}
          className="rounded-md bg-white text-accent text-sm font-medium px-4 py-2 hover:bg-white/90 disabled:opacity-50"
        >
          {ending ? "Ending…" : "End call"}
        </button>
      </div>
    </div>
  );
}