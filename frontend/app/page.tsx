"use client";

import { useCallback, useEffect, useState } from "react";

import { CallHistoryList } from "@/components/caregiver/CallHistoryList";
import { HealthSnapshotCard } from "@/components/caregiver/HealthSnapshotCard";
import { PatientCallPanel } from "@/components/caregiver/PatientCallPanel";
import { TodaysMedicationsCard } from "@/components/caregiver/TodaysMedicationsCard";
import { Nav } from "@/components/shared/Nav";
import { getHealthSnapshot, listCalls, listTodaysDoses } from "@/lib/api";
import { usePrimaryContext } from "@/lib/hooks";
import type { CallSummary, DoseWithCall, HealthSnapshot as HealthSnapshotT } from "@/lib/types";

export default function Home() {
  const { caregiver, patient, loading, error } = usePrimaryContext();
  const [doses, setDoses] = useState<DoseWithCall[]>([]);
  const [snapshot, setSnapshot] = useState<HealthSnapshotT | null>(null);
  const [aiCalls, setAiCalls] = useState<CallSummary[]>([]);
  const [caregiverCalls, setCaregiverCalls] = useState<CallSummary[]>([]);

  const refresh = useCallback(async () => {
    console.log("🔄 Refreshing data...");
    
    if (!patient) {
      console.warn("⚠️ No patient available for refresh");
      return;
    }
    
    // ✅ Get the patient ID
    const patientId = patient.patient_id || patient.id;
    console.log("🔑 Patient ID for refresh:", patientId);
    
    if (!patientId) {
      console.error("❌ Patient has no ID:", patient);
      return;
    }
    
    try {
      console.log("📡 Fetching data for patient:", patientId);
      const [d, s, ai, cg] = await Promise.all([
        listTodaysDoses(patientId),
        getHealthSnapshot(patientId),
        listCalls({ patientId, direction: "system", limit: 5 }),
        listCalls({ patientId, direction: "caregiver", limit: 5 }),
      ]);
      console.log("✅ Data fetched successfully");
      setDoses(d || []);
      setSnapshot(s);
      setAiCalls(ai || []);
      setCaregiverCalls(cg || []);
    } catch (err) {
      console.error("❌ Error refreshing data:", err);
    }
  }, [patient]);

  useEffect(() => {
    console.log("🔄 Home component mounted");
    refresh();
    const timer = setInterval(refresh, 5000);
    return () => {
      console.log("🧹 Cleaning up timer");
      clearInterval(timer);
    };
  }, [refresh]);

  if (loading) {
    console.log("⏳ Loading...");
    return <div className="min-h-screen flex items-center justify-center text-sm text-muted">Loading…</div>;
  }
  
  if (error) {
    console.error("❌ Error state:", error);
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-clay text-center px-6">
        {error}
      </div>
    );
  }
  
  if (!patient) {
    console.warn("⚠️ No patient available");
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-clay text-center px-6">
        No patient found. Run the backend seed script: python -m app.seed
      </div>
    );
  }

  if (!caregiver) {
    console.warn("⚠️ No caregiver available");
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-clay text-center px-6">
        No caregiver found. Run the backend seed script: python -m app.seed
      </div>
    );
  }

  // ✅ Get the caregiver ID
  const caregiverId = caregiver.caregiver_id || caregiver.id;
  console.log("👤 Caregiver ID:", caregiverId);
  console.log("👤 Patient ID:", patient.patient_id);

  return (
    <div className="min-h-screen">
      <Nav caregiverName={caregiver.name} />
      <main className="mx-auto max-w-5xl px-4 sm:px-8 py-8 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        <PatientCallPanel patient={patient} caregiverId={caregiverId} onCallPlaced={refresh} />
        <div className="flex flex-col gap-6">
          <TodaysMedicationsCard doses={doses} />
          {snapshot && <HealthSnapshotCard snapshot={snapshot} />}
          <CallHistoryList title="Recent AI calls" calls={aiCalls} emptyText="No AI calls yet." />
          <CallHistoryList title="Your previous calls" calls={caregiverCalls} emptyText="You haven't called yet." />
        </div>
      </main>
    </div>
  );
}