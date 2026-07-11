// hooks/useCalls.ts
import { useEffect, useState } from "react";
import type { CallSummary } from "@/lib/types";
import { listCalls, listLiveCalls } from "@/lib/api";

export function useCalls(patientId?: string) {
  const [calls, setCalls] = useState<CallSummary[]>([]);
  const [liveCalls, setLiveCalls] = useState<CallSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    if (!patientId) {
      setLoading(false);
      return;
    }

    try {
      const [allCalls, live] = await Promise.all([
        listCalls({ patientId }),
        listLiveCalls(patientId),
      ]);
      setCalls(allCalls);
      setLiveCalls(live);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load calls");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [patientId]);

  return { calls, liveCalls, loading, error, refreshCalls: loadData };
}