"use client";

import { useCallback, useEffect, useState } from "react";

import { CallHistoryList } from "@/components/caregiver/CallHistoryList";
import { HealthSnapshotCard } from "@/components/caregiver/HealthSnapshotCard";
import { PatientCallPanel } from "@/components/caregiver/PatientCallPanel";
import { TodaysMedicationsCard } from "@/components/caregiver/TodaysMedicationsCard";
import { Nav } from "@/components/shared/Nav";
import { getHealthSnapshot, listCalls, listTodaysDoses } from "@/lib/api";
import type { CallSummary, DoseWithCall, HealthSnapshot as HealthSnapshotT, Patient, Caregiver } from "@/lib/types";

// ✅ Hardcoded patient and caregiver data from your database
const FALLBACK_PATIENT: Patient = {
  patient_id: "2b743549-3ed4-45f9-852d-afe1e6e5fbd5",
  name: "Robert Mitchell",
  date_of_birth: "1955-07-07",
  age: 71,
  relation_to_caregiver: "Your father",
  phone_number: "+15550002222",
  phone_label: "Primary · Mobile",
  ai_monitoring_enabled: true,
  last_hba1c: 7.2,
  last_hba1c_at: "2026-06-25",
  primary_caregiver_id: "f4ecf73b-387d-48bf-a5d9-188490d6547b",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const FALLBACK_CAREGIVER: Caregiver = {
  caregiver_id: "f4ecf73b-387d-48bf-a5d9-188490d6547b",
  name: "Sarah Mitchell",
  email: "sarah@example.com",
  phone_number: "+15550001111",
  created_at: new Date().toISOString(),
};

export default function Home() {
  const [doses, setDoses] = useState<DoseWithCall[]>([]);
  const [snapshot, setSnapshot] = useState<HealthSnapshotT | null>(null);
  const [aiCalls, setAiCalls] = useState<CallSummary[]>([]);
  const [caregiverCalls, setCaregiverCalls] = useState<CallSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const patient = FALLBACK_PATIENT;
  const caregiver = FALLBACK_CAREGIVER;

  const refresh = useCallback(async () => {
    const patientId = patient.patient_id;
    try {
      const [d, s, ai, cg] = await Promise.all([
        listTodaysDoses(patientId),
        getHealthSnapshot(patientId),
        listCalls({ patientId, direction: "system", limit: 5 }),
        listCalls({ patientId, direction: "caregiver", limit: 5 }),
      ]);
      setDoses(d || []);
      setSnapshot(s);
      setAiCalls(ai || []);
      setCaregiverCalls(cg || []);
    } catch (err) {
      console.error("Error refreshing data:", err);
    }
  }, [patient]);

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
        <PatientCallPanel patient={patient} caregiverId={caregiver.caregiver_id} onCallPlaced={refresh} />
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