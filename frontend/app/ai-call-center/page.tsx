"use client";

import { useCallback, useEffect, useState } from "react";

import { CallLogTable } from "@/components/call-center/CallLogTable";
import { LiveCallBanner } from "@/components/call-center/LiveCallBanner";
import { ResponseBreakdown } from "@/components/call-center/ResponseBreakdown";
import { StatCards } from "@/components/call-center/StatCards";
import { TodaysScheduleCard } from "@/components/call-center/TodaysScheduleCard";
import { Nav } from "@/components/shared/Nav";
import { getDashboardStats, listCalls, listLiveCalls, listTodaysDoses } from "@/lib/api";
import { FALLBACK_PATIENT, FALLBACK_CAREGIVER, PATIENT_ID } from "@/lib/constants";
import type { CallSummary, DashboardStats, DoseWithCall } from "@/lib/types";

export default function AiCallCenterPage() {
  const [liveCalls, setLiveCalls] = useState<CallSummary[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [callLog, setCallLog] = useState<CallSummary[]>([]);
  const [doses, setDoses] = useState<DoseWithCall[]>([]);
  const [loading, setLoading] = useState(true);

  // ✅ Use hardcoded data
  const patient = FALLBACK_PATIENT;
  const caregiver = FALLBACK_CAREGIVER;

  const refresh = useCallback(async () => {
    try {
      const [live, s, log, d] = await Promise.all([
        listLiveCalls(PATIENT_ID),
        getDashboardStats(PATIENT_ID),
        listCalls({ patientId: PATIENT_ID, direction: "system", limit: 20 }),
        listTodaysDoses(PATIENT_ID),
      ]);
      
      setLiveCalls(live || []);
      setStats(s);
      setCallLog(log || []);
      setDoses(d || []);
    } catch (err) {
      console.error("Error refreshing data:", err);
    }
  }, []);

  useEffect(() => {
    setLoading(false);
    refresh();
    const timer = setInterval(refresh, 4000);
    return () => clearInterval(timer);
  }, [refresh]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-sm text-muted">Loading…</div>;
  }

  return (
    <div className="min-h-screen">
      <Nav caregiverName={caregiver.name} />
      <main className="mx-auto max-w-5xl px-4 sm:px-8 py-8 flex flex-col gap-6">
        <header>
          <p className="text-2xs font-mono uppercase tracking-wide text-accent">AI Call Center</p>
          <h1 className="text-xl font-semibold text-ink tracking-tight">
            Automated medication monitoring — {patient.name}
          </h1>
          <p className="text-sm text-muted mt-0.5">Scheduled system-to-patient calls, updated in real time.</p>
        </header>

        {liveCalls.map((call) => (
          <LiveCallBanner key={call.call_id} call={call} onEnded={refresh} />
        ))}

        {stats && <StatCards stats={stats} />}

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
          <CallLogTable calls={callLog} />
          <div className="flex flex-col gap-6">
            <TodaysScheduleCard doses={doses} onCallPlaced={refresh} />
            {stats && <ResponseBreakdown breakdown={stats.breakdown} periodDays={stats.period_days} />}
          </div>
        </div>
      </main>
    </div>
  );
}