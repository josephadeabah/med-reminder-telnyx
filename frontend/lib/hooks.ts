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
        console.log("🔍 Fetching caregiver and patients...");
        
        const [cg, patients] = await Promise.all([
          getCurrentCaregiver(), 
          listPatients()
        ]);
        
        if (cancelled) return;
        
        console.log("📋 Caregiver response:", cg);
        console.log("📋 Patients response:", patients);
        
        // ✅ Set caregiver
        if (cg) {
          const caregiverData: Caregiver = {
            caregiver_id: cg.caregiver_id || cg.id || "",
            name: cg.name || "",
            email: cg.email || "",
            phone_number: cg.phone_number || "",
            created_at: cg.created_at || new Date().toISOString(),
          };
          console.log("✅ Set caregiver:", caregiverData);
          setCaregiver(caregiverData);
        } else {
          console.warn("⚠️ No caregiver found");
        }
        
        // ✅ Set patient - CRITICAL FIX
        if (patients && Array.isArray(patients) && patients.length > 0) {
          const p = patients[0];
          console.log("📋 First patient from API:", p);
          
          // Make sure we use the correct field name
          const patientId = p.patient_id || p.id || p.patientId;
          console.log("🔑 Patient ID:", patientId);
          
          if (!patientId) {
            console.error("❌ Patient has no ID:", p);
            setError("Patient has no ID field");
            return;
          }
          
          const patientData: Patient = {
            patient_id: patientId,
            name: p.name || "",
            date_of_birth: p.date_of_birth || null,
            age: p.age || null,
            relation_to_caregiver: p.relation_to_caregiver || null,
            phone_number: p.phone_number || "",
            phone_label: p.phone_label || "Primary · Mobile",
            ai_monitoring_enabled: p.ai_monitoring_enabled ?? true,
            last_hba1c: p.last_hba1c || null,
            last_hba1c_at: p.last_hba1c_at || null,
            primary_caregiver_id: p.primary_caregiver_id || null,
            created_at: p.created_at || new Date().toISOString(),
            updated_at: p.updated_at || new Date().toISOString(),
          };
          
          console.log("✅ Set patient:", patientData);
          setPatient(patientData);
        } else {
          console.warn("⚠️ No patients found in response");
          setError("No patients found. Run the backend seed script.");
        }
      } catch (err) {
        console.error("❌ Error in usePrimaryContext:", err);
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) {
          console.log("🏁 Loading complete");
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { caregiver, patient, error, loading };
}