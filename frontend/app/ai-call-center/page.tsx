// app/ai-call-center/page.tsx
"use client";

import { usePrimaryContext } from "@/hooks/usePrimaryContext";
import { CallLogTable } from "@/components/CallLogTable";
import { LiveCallBanner } from "@/components/LiveCallBanner";
import { Nav } from "@/components/Nav";
import { TodaysScheduleCard } from "@/components/TodaysScheduleCard";
import { StatCards } from "@/components/StatCards";
import { ResponseBreakdown } from "@/components/ResponseBreakdown";
import { HealthSnapshotCard } from "@/components/HealthSnapshotCard";
import { CallHistoryList } from "@/components/CallHistoryList";
import { useCalls } from "@/hooks/useCalls";
import { useDoses } from "@/hooks/useDoses";
import { useDashboard } from "@/hooks/useDashboard";

export default function AICallCenterPage() {
  const { caregiver, patient, loading, error } = usePrimaryContext();
  const { calls, liveCalls, refreshCalls } = useCalls(patient?.patient_id);
  const { doses, refreshDoses } = useDoses(patient?.patient_id);
  const { stats, snapshot, refreshDashboard } = useDashboard(patient?.patient_id);

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

  const handleCallPlaced = () => {
    refreshCalls();
    refreshDoses();
    refreshDashboard();
  };

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
            <h1 className="text-xl font-semibold text-ink">AI Call Center</h1>
            <p className="text-sm text-muted">
              {patient.name} · {patient.age} years old
            </p>
          </div>
        </div>

        {/* Live call banner */}
        {liveCalls.length > 0 && (
          <LiveCallBanner call={liveCalls[0]} onEnded={handleCallPlaced} />
        )}

        {/* Stats */}
        {stats && <StatCards stats={stats} />}

        {/* Today's schedule */}
        <TodaysScheduleCard doses={doses} onCallPlaced={handleCallPlaced} />

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {snapshot && <HealthSnapshotCard snapshot={snapshot} />}
          {stats?.breakdown && (
            <ResponseBreakdown breakdown={stats.breakdown} periodDays={stats.period_days} />
          )}
        </div>

        {/* Call history */}
        <CallHistoryList
          title="Recent calls"
          calls={calls.slice(0, 10)}
          emptyText="No calls yet."
        />

        {/* Full call log */}
        <CallLogTable calls={calls} />
      </main>
    </div>
  );
}