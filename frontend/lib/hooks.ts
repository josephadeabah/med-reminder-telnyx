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
        console.log("Fetching caregiver and patients...");
        const [cg, patients] = await Promise.all([getCurrentCaregiver(), listPatients()]);
        
        if (cancelled) return;
        
        console.log("Caregiver response:", cg);
        console.log("Patients response:", patients);
        
        setCaregiver(cg);
        
        if (patients && Array.isArray(patients) && patients.length > 0) {
          const firstPatient = patients[0];
          console.log("Setting patient:", firstPatient);
          console.log("Patient ID:", firstPatient.patient_id || firstPatient.id);
          setPatient(firstPatient);
        } else {
          console.warn("No patients found - seeding may not have run");
          setError("No patients found. Run the backend seed script.");
        }
      } catch (err) {
        console.error("Error in usePrimaryContext:", err);
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