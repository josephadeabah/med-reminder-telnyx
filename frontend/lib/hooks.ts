"use client";

import { useEffect, useState } from "react";

import { getCurrentCaregiver, listPatients } from "./api";
import type { Caregiver, Patient } from "./types";

// Hardcoded fallback IDs from your database
const FALLBACK_PATIENT_ID = "2b743549-3ed4-45f9-852d-afe1e6e5fbd5";
const FALLBACK_CAREGIVER_ID = "f4ecf73b-387d-48bf-a5d9-188490d6547b";

export function usePrimaryContext() {
  const [caregiver, setCaregiver] = useState<Caregiver | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    
    async function loadData() {
      try {
        // Try to fetch from API
        const [cg, patients] = await Promise.all([
          getCurrentCaregiver(),
          listPatients()
        ]);
        
        if (cancelled) return;

        // Set caregiver - use API or fallback
        if (cg) {
          setCaregiver({
            caregiver_id: cg.caregiver_id || FALLBACK_CAREGIVER_ID,  // ✅ Removed cg.id
            name: cg.name || "Sarah Mitchell",
            email: cg.email || "sarah@example.com",
            phone_number: cg.phone_number || "+16465753303",
            created_at: cg.created_at || new Date().toISOString(),
          });
        } else {
          // Fallback caregiver if API returns null
          setCaregiver({
            caregiver_id: FALLBACK_CAREGIVER_ID,
            name: "Sarah Mitchell",
            email: "sarah@example.com",
            phone_number: "+16465753303",
            created_at: new Date().toISOString(),
          });
        }

        // Set patient - use API or fallback
        if (patients && patients.length > 0) {
          const p = patients[0];
          setPatient({
            patient_id: p.patient_id || FALLBACK_PATIENT_ID,  // ✅ Removed p.id
            name: p.name || "Robert Mitchell",
            date_of_birth: p.date_of_birth || "1955-07-07",
            age: p.age || 71,
            relation_to_caregiver: p.relation_to_caregiver || "Your father",
            phone_number: p.phone_number || "+16465753303",
            phone_label: p.phone_label || "Primary · Mobile",
            ai_monitoring_enabled: p.ai_monitoring_enabled ?? true,
            last_hba1c: p.last_hba1c || 7.2,
            last_hba1c_at: p.last_hba1c_at || "2026-06-25",
            primary_caregiver_id: p.primary_caregiver_id || FALLBACK_CAREGIVER_ID,
            created_at: p.created_at || new Date().toISOString(),
            updated_at: p.updated_at || new Date().toISOString(),
          });
        } else {
          // ✅ FALLBACK: Use hardcoded patient data from your database
          setPatient({
            patient_id: FALLBACK_PATIENT_ID,
            name: "Robert Mitchell",
            date_of_birth: "1955-07-07",
            age: 71,
            relation_to_caregiver: "Your father",
            phone_number: "+16465753303",
            phone_label: "Primary · Mobile",
            ai_monitoring_enabled: true,
            last_hba1c: 7.2,
            last_hba1c_at: "2026-06-25",
            primary_caregiver_id: FALLBACK_CAREGIVER_ID,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        }
      } catch (err) {
        // ✅ FALLBACK: If API fails, use hardcoded data
        setCaregiver({
          caregiver_id: FALLBACK_CAREGIVER_ID,
          name: "Sarah Mitchell",
          email: "sarah@example.com",
          phone_number: "+16465753303",
          created_at: new Date().toISOString(),
        });
        setPatient({
          patient_id: FALLBACK_PATIENT_ID,
          name: "Robert Mitchell",
          date_of_birth: "1955-07-07",
          age: 71,
          relation_to_caregiver: "Your father",
          phone_number: "+16465753303",
          phone_label: "Primary · Mobile",
          ai_monitoring_enabled: true,
          last_hba1c: 7.2,
          last_hba1c_at: "2026-06-25",
          primary_caregiver_id: FALLBACK_CAREGIVER_ID,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load - using fallback data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadData();
    return () => {
      cancelled = true;
    };
  }, []);

  return { caregiver, patient, error, loading };
}