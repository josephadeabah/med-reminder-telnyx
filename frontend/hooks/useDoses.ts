// hooks/useDoses.ts
import { useEffect, useState } from "react";
import type { DoseWithCall } from "@/lib/types";
import { listTodaysDoses } from "@/lib/api";

export function useDoses(patientId?: string) {
  const [doses, setDoses] = useState<DoseWithCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    if (!patientId) {
      setLoading(false);
      return;
    }

    try {
      const data = await listTodaysDoses(patientId);
      setDoses(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load doses");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [patientId]);

  return { doses, loading, error, refreshDoses: loadData };
}