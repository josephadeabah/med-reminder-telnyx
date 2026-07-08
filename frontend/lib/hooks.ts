"use client";

import { useEffect, useState } from "react";

import { getCurrentCaregiver, listPatients } from "./api";
import type { Caregiver, Patient } from "./types";

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
        
        console.log("Caregiver response:", cg);
        console.log("Patients response:", patients);
        
        // ✅ Map the caregiver response
        if (cg) {
          setCaregiver({
            caregiver_id: cg.caregiver_id || cg.id || cg.caregiverId,
            name: cg.name,
            email: cg.email,
            phone_number: cg.phone_number,
            created_at: cg.created_at,
          });
        }
        
        // ✅ Map the patient response
        if (patients && Array.isArray(patients) && patients.length > 0) {
          const p = patients[0];
          const patientData = {
            patient_id: p.patient_id || p.id || p.patientId,
            name: p.name,
            date_of_birth: p.date_of_birth,
            age: p.age,
            relation_to_caregiver: p.relation_to_caregiver,
            phone_number: p.phone_number,
            phone_label: p.phone_label,
            ai_monitoring_enabled: p.ai_monitoring_enabled,
            last_hba1c: p.last_hba1c,
            last_hba1c_at: p.last_hba1c_at,
            primary_caregiver_id: p.primary_caregiver_id,
            created_at: p.created_at,
            updated_at: p.updated_at,
          };
          console.log("Set patient:", patientData);
          setPatient(patientData);
        } else {
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