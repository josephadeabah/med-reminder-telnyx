"use client";

import { useCallback, useEffect, useState } from "react";

import { CallHistoryList } from "@/components/caregiver/CallHistoryList";
import { HealthSnapshotCard } from "@/components/caregiver/HealthSnapshotCard";
import { PatientCallPanel } from "@/components/caregiver/PatientCallPanel";
import { TodaysMedicationsCard } from "@/components/caregiver/TodaysMedicationsCard";
import { Nav } from "@/components/shared/Nav";
import { getHealthSnapshot, listCalls, listTodaysDoses } from "@/lib/api";
import { FALLBACK_PATIENT, FALLBACK_CAREGIVER, PATIENT_ID, CAREGIVER_ID } from "@/lib/constants";
import type { CallSummary, DoseWithCall, HealthSnapshot as HealthSnapshotT } from "@/lib/types";

export default function Home() {
  const [doses, setDoses] = useState<DoseWithCall[]>([]);
  const [snapshot, setSnapshot] = useState<HealthSnapshotT | null>(null);
  const [aiCalls, setAiCalls] = useState<CallSummary[]>([]);
  const [caregiverCalls, setCaregiverCalls] = useState<CallSummary[]>([]);
  const [loading, setLoading] = useState(true);

  // ✅ Use hardcoded data - guaranteed to work
  const patient = FALLBACK_PATIENT;
  const caregiver = FALLBACK_CAREGIVER;

  const refresh = useCallback(async () => {
    try {
      console.log("🔄 Fetching data for patient:", PATIENT_ID);
      
      const [d, s, ai, cg] = await Promise.all([
        listTodaysDoses(PATIENT_ID),
        getHealthSnapshot(PATIENT_ID),
        listCalls({ patientId: PATIENT_ID, direction: "system", limit: 5 }),
        listCalls({ patientId: PATIENT_ID, direction: "caregiver", limit: 5 }),
      ]);
      
      setDoses(d || []);
      setSnapshot(s);
      setAiCalls(ai || []);
      setCaregiverCalls(cg || []);
    } catch (err) {
      console.error("❌ Error refreshing data:", err);
    }
  }, []);

  useEffect(() => {
    setLoading(false);
    refresh();
    const timer = setInterval(refresh, 5000);
    return () => clearInterval(timer);
  }, [refresh]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-sm text-muted">Loading…</div>;
  }

  return (
    <div className="min-h-screen">
      <Nav caregiverName={caregiver.name} />
      <main className="mx-auto max-w-5xl px-4 sm:px-8 py-8 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        <PatientCallPanel patient={patient} caregiverId={CAREGIVER_ID} onCallPlaced={refresh} />
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