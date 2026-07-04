"use client";

import { useEffect, useState } from "react";

import { getCurrentCaregiver, listPatients } from "./api";
import type { Caregiver, Patient } from "./types";

/**
 * Resolves "the current caregiver" and "the active patient" for the demo.
 * Stands in for real auth/patient-switching - see backend's
 * caregivers/router.py::get_current_caregiver for the matching stub on
 * the API side. Both sides are meant to be swapped together later.
 */
export function usePrimaryContext() {
  const [caregiver, setCaregiver] = useState<Caregiver | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [cg, patients] = await Promise.all([getCurrentCaregiver(), listPatients()]);
        if (cancelled) return;
        setCaregiver(cg);
        setPatient(patients[0] ?? null);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { caregiver, patient, error, loading };
}
