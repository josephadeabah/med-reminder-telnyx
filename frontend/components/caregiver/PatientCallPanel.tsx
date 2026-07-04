"use client";

import { useState } from "react";
import type { CallReason, CallType, Patient } from "@/lib/types";
import { ApiError, placeCaregiverCall } from "@/lib/api";

const REASONS: { value: CallReason; label: string }[] = [
  { value: "medication_check", label: "Medication check" },
  { value: "wellbeing_check", label: "Wellbeing check-in" },
  { value: "appointment_reminder", label: "Appointment reminder" },
  { value: "general_check", label: "General check-in" },
  { value: "urgent_concern", label: "Urgent concern" },
];

export function PatientCallPanel({
  patient,
  caregiverId,
  onCallPlaced,
}: {
  patient: Patient;
  caregiverId: string;
  onCallPlaced: () => void;
}) {
  const [callType, setCallType] = useState<CallType>("voice");
  const [reason, setReason] = useState<CallReason | null>(null);
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [placed, setPlaced] = useState(false);

  async function startCall() {
    setError(null);
    setSubmitting(true);
    try {
      await placeCaregiverCall({
        patient_id: patient.id,
        caregiver_id: caregiverId,
        call_type: callType,
        call_reason: reason,
        pre_call_note: note.trim() || null,
      });
      setPlaced(true);
      setNote("");
      setReason(null);
      onCallPlaced();
      setTimeout(() => setPlaced(false), 4000);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't reach the backend. Is it running?");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="rounded-xl border border-line bg-surface overflow-hidden">
      <div className="px-6 pt-6 pb-4 border-b border-line">
        <h1 className="text-xl font-semibold text-ink tracking-tight">Call {patient.name}</h1>
        <p className="text-sm text-muted mt-0.5">
          Direct caregiver-to-patient call — logged to {patient.name.split(" ")[0]}&apos;s health timeline automatically
        </p>
      </div>

      <div className="p-6 flex flex-col gap-6">
        {/* Patient card */}
        <div className="flex items-center gap-4 rounded-lg border border-line p-4">
          <div className="h-11 w-11 rounded-full bg-accent-soft text-accent flex items-center justify-center font-semibold shrink-0">
            {patient.name.charAt(0)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-ink">{patient.name}</p>
            <p className="text-2xs font-mono text-muted">
              {patient.age ? `${patient.age} years old` : ""}
              {patient.relation_to_caregiver ? ` · ${patient.relation_to_caregiver}` : ""}
            </p>
          </div>
          <div className="text-right shrink-0">
            <p className="text-sm font-mono text-ink">{patient.phone_number}</p>
            <p className="text-2xs font-mono text-muted">{patient.phone_label}</p>
          </div>
        </div>

        {/* Call type */}
        <div>
          <p className="text-2xs font-mono uppercase tracking-wide text-muted mb-2">Call type</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setCallType("voice")}
              className={`text-left rounded-lg border px-4 py-3 transition-colors ${
                callType === "voice" ? "border-accent bg-accent-soft" : "border-line hover:border-muted"
              }`}
            >
              <p className="text-sm font-medium text-ink">Voice call</p>
              <p className="text-2xs text-muted mt-0.5">Audio only — works on any phone. Best for {patient.name.split(" ")[0]}.</p>
            </button>
            <button
              type="button"
              onClick={() => setCallType("video")}
              className={`text-left rounded-lg border px-4 py-3 transition-colors ${
                callType === "video" ? "border-accent bg-accent-soft" : "border-line hover:border-muted"
              }`}
            >
              <p className="text-sm font-medium text-ink">Video call</p>
              <p className="text-2xs text-muted mt-0.5">
                Requires {patient.name.split(" ")[0]} to have the companion app
              </p>
            </button>
          </div>
        </div>

        {/* Call reason */}
        <div>
          <p className="text-2xs font-mono uppercase tracking-wide text-muted mb-2">Call reason (optional)</p>
          <div className="flex flex-wrap gap-2">
            {REASONS.map((r) => (
              <button
                key={r.value}
                type="button"
                onClick={() => setReason(reason === r.value ? null : r.value)}
                className={`text-2xs font-medium px-3 py-1.5 rounded-full border transition-colors ${
                  reason === r.value
                    ? "border-accent bg-accent-soft text-accent"
                    : "border-line text-muted hover:text-ink hover:border-muted"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Pre-call note */}
        <div>
          <label htmlFor="pre_call_note" className="text-2xs font-mono uppercase tracking-wide text-muted mb-2 block">
            Private pre-call note
          </label>
          <textarea
            id="pre_call_note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            maxLength={2000}
            placeholder={`Add a private pre-call note — won't be shared with ${patient.name.split(" ")[0]}...`}
            className="w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted resize-none focus-visible:border-accent"
          />
        </div>

        {error && <div className="rounded-lg border border-clay/30 bg-clay-soft px-4 py-3 text-sm text-clay">{error}</div>}
        {placed && (
          <div className="rounded-lg border border-accent/30 bg-accent-soft px-4 py-3 text-sm text-accent">
            Call placed — dialing you now, then connecting you to {patient.name}.
          </div>
        )}

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={startCall}
            disabled={submitting}
            className="flex items-center gap-2 rounded-md bg-accent text-white text-sm font-medium px-5 py-2.5 hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? "Placing call…" : "Start call"}
          </button>
          <p className="text-2xs font-mono text-muted">Calls are logged automatically to {patient.name.split(" ")[0]}&apos;s health timeline.</p>
        </div>
      </div>
    </div>
  );
}
