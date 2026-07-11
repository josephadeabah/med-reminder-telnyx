// hooks/useDashboard.ts
import { useEffect, useState } from "react";
import type { DashboardStats, HealthSnapshot } from "@/lib/types";
import { getDashboardStats, getHealthSnapshot } from "@/lib/api";

export function useDashboard(patientId?: string) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [snapshot, setSnapshot] = useState<HealthSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    if (!patientId) {
      setLoading(false);
      return;
    }

    try {
      const [statsData, snapshotData] = await Promise.all([
        getDashboardStats(patientId),
        getHealthSnapshot(patientId),
      ]);
      setStats(statsData);
      setSnapshot(snapshotData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, [patientId]);

  return { stats, snapshot, loading, error, refreshDashboard: loadData };
}