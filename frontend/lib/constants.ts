// lib/constants.ts
import type { Patient, Caregiver } from "./types";

// These IDs come from your database - from your debug output
export const PATIENT_ID = "2b743549-3ed4-45f9-852d-afe1e6e5fbd5";
export const CAREGIVER_ID = "f4ecf73b-387d-48bf-a5d9-188490d6547b";

export const FALLBACK_PATIENT: Patient = {
  patient_id: PATIENT_ID,
  name: "Robert Mitchell",
  date_of_birth: "1955-07-07",
  age: 71,
  relation_to_caregiver: "Your father",
  phone_number: "+233200415683",
  phone_label: "Primary · Mobile",
  ai_monitoring_enabled: true,
  last_hba1c: 7.2,
  last_hba1c_at: "2026-06-25",
  primary_caregiver_id: CAREGIVER_ID,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export const FALLBACK_CAREGIVER: Caregiver = {
  caregiver_id: CAREGIVER_ID,
  name: "Sarah Mitchell",
  email: "sarah@example.com",
  phone_number: "+233200415683",
  created_at: new Date().toISOString(),
};