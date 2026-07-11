"use client";

import { useState } from "react";
import { triggerEscalation } from "@/lib/api";
import { ApiError } from "@/lib/api";

interface EmergencyButtonsProps {
  patientId: string;
  patientName: string;
  caregiverPhoneNumber?: string;
  caregiverName?: string;
}

export function EmergencyButtons({
  patientId,
  patientName,
  caregiverPhoneNumber,
  caregiverName,
}: EmergencyButtonsProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleEmergency = async (eventType: string, reason: string) => {
    setLoading(eventType);
    setError(null);
    setSuccess(null);

    try {
      await triggerEscalation({
        patient_id: patientId,
        event_type: eventType,
        reason: reason,
      });
      setSuccess(`✅ Emergency alert sent for: ${reason}`);
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to send alert");
      setTimeout(() => setError(null), 5000);
    } finally {
      setLoading(null);
    }
  };

  const handleCallCaregiver = () => {
    if (!caregiverPhoneNumber) {
      alert("⚠️ No caregiver phone number configured.");
      return;
    }
    window.location.href = `tel:${caregiverPhoneNumber}`;
  };

  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <h2 className="text-2xs font-mono uppercase tracking-wide text-muted mb-3">
        🚨 Emergency Actions
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <button
          onClick={() =>
            handleEmergency("feeling_giddy", `${patientName} is feeling giddy/dizzy`)
          }
          disabled={!!loading}
          className="rounded-lg bg-clay-soft border border-clay/30 px-4 py-3 text-sm font-medium text-clay hover:bg-clay-soft/70 disabled:opacity-50 transition-colors"
        >
          {loading === "feeling_giddy" ? "⏳ Sending..." : "🤢 Feeling Giddy"}
        </button>

        <button
          onClick={() =>
            handleEmergency("out_of_medicines", `${patientName} is out of medicines`)
          }
          disabled={!!loading}
          className="rounded-lg bg-amber-soft border border-amber/30 px-4 py-3 text-sm font-medium text-amber hover:bg-amber-soft/70 disabled:opacity-50 transition-colors"
        >
          {loading === "out_of_medicines" ? "⏳ Sending..." : "💊 Out of Medicines"}
        </button>

        <button
          onClick={() =>
            handleEmergency("symptom_report", `${patientName} reported concerning symptoms`)
          }
          disabled={!!loading}
          className="rounded-lg bg-clay-soft border border-clay/30 px-4 py-3 text-sm font-medium text-clay hover:bg-clay-soft/70 disabled:opacity-50 transition-colors sm:col-span-2"
        >
          {loading === "symptom_report" ? "⏳ Sending..." : "⚠️ Report Symptoms"}
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-clay/30 bg-clay-soft px-4 py-2 text-sm text-clay mb-3">
          ❌ {error}
        </div>
      )}
      {success && (
        <div className="rounded-lg border border-accent/30 bg-accent-soft px-4 py-2 text-sm text-accent mb-3">
          {success}
        </div>
      )}

      <div className="flex items-center gap-3 pt-3 border-t border-line">
        <button
          onClick={handleCallCaregiver}
          disabled={!caregiverPhoneNumber}
          className="flex items-center gap-2 rounded-md bg-accent text-white text-sm font-medium px-5 py-2.5 hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          📞 Call {caregiverName || "Caregiver"}
        </button>
        {caregiverPhoneNumber && (
          <span className="text-2xs font-mono text-muted">
            {caregiverPhoneNumber}
          </span>
        )}
        {!caregiverPhoneNumber && (
          <span className="text-2xs font-mono text-clay">
            ⚠️ No caregiver configured
          </span>
        )}
      </div>
      <p className="text-2xs text-muted mt-2">
        This will open your device&apos;s dialer. You&apos;ll need to press &quot;Call&quot; to connect.
      </p>
    </div>
  );
}