// app/page.tsx
"use client";

import { usePrimaryContext } from "@/hooks/usePrimaryContext";
import { EmergencyButtons } from "@/components/EmergencyButtons";
import { CallLogTable } from "@/components/CallLogTable";
import { LiveCallBanner } from "@/components/LiveCallBanner";
import { Nav } from "@/components/Nav";
import { useCalls } from "@/hooks/useCalls";

export default function HomePage() {
  const { caregiver, patient, loading, error } = usePrimaryContext();
  const { calls, liveCalls, refreshCalls } = useCalls(patient?.patient_id);

  if (loading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="text-muted">Loading...</div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="text-clay">Error: {error || "Patient not found"}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper">
      <Nav caregiverName={caregiver?.name} />

      <main className="mx-auto max-w-5xl px-4 sm:px-8 py-8 space-y-6">
        {/* Patient header */}
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-full bg-accent-soft text-accent flex items-center justify-center font-semibold text-lg">
            {patient.name.charAt(0)}
          </div>
          <div>
            <h1 className="text-xl font-semibold text-ink">{patient.name}</h1>
            <p className="text-sm text-muted">
              {patient.age} years old · {patient.relation_to_caregiver || "Patient"}
            </p>
          </div>
        </div>

        {/* Live call banner */}
        {liveCalls.length > 0 && (
          <LiveCallBanner call={liveCalls[0]} onEnded={refreshCalls} />
        )}

        {/* Emergency buttons */}
        <EmergencyButtons
          patientId={patient.patient_id}
          patientName={patient.name}
          caregiverPhoneNumber={caregiver?.phone_number}
          caregiverName={caregiver?.name}
        />

        {/* Call log */}
        <CallLogTable calls={calls} />
      </main>
    </div>
  );
}