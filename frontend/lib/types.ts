export type CallDirection = "system" | "caregiver";
export type CallType = "voice" | "video";
export type CallReason = "medication_check" | "wellbeing_check" | "appointment_reminder" | "general_check" | "urgent_concern";
export type CallStatus =
  | "queued" | "initiated" | "ringing" | "answered" | "bridged"
  | "completed" | "failed" | "busy" | "no-answer" | string;
export type CallIntent = "taken" | "not_taken" | "unknown" | null;
export type DoseStatus = "pending" | "confirmed" | "missed" | "skipped" | "escalated" | string;

export interface Patient {
  id: string;
  name: string;
  date_of_birth: string | null;
  age: number | null;
  relation_to_caregiver: string | null;
  phone_number: string;
  phone_label: string;
  ai_monitoring_enabled: boolean;
  last_hba1c: number | null;
  last_hba1c_at: string | null;
  primary_caregiver_id: string | null;
}

export interface Caregiver {
  id: string;
  name: string;
  email: string;
  phone_number: string;
}

export interface HealthSnapshot {
  adherence_30day_pct: number | null;
  next_appointment_at: string | null;
  next_appointment_doctor: string | null;
  last_hba1c: number | null;
  last_hba1c_at: string | null;
  next_refill_medication: string | null;
  next_refill_days_remaining: number | null;
}

export interface DoseWithCall {
  id: string;
  patient_id: string;
  medication_id: string;
  medication_name: string;
  medication_dose_text: string;
  schedule_label: string;
  scheduled_for: string;
  status: DoseStatus;
  call_id: string | null;
  call_status: CallStatus | null;
  call_intent: CallIntent;
  call_transcript: string | null;
}

export interface CallEvent {
  event_type: string;
  leg: string | null;
  payload: string | null;
  created_at: string;
}

export interface CallDetail {
  id: string;
  patient_id: string;
  caregiver_id: string | null;
  dose_id: string | null;
  direction: CallDirection;
  call_type: CallType;
  call_reason: CallReason | null;
  pre_call_note: string | null;
  call_control_id: string | null;
  patient_call_control_id: string | null;
  status: CallStatus;
  intent: CallIntent;
  transcript: string | null;
  created_at: string;
  updated_at: string;
  events: CallEvent[];
}

export interface CallSummary {
  id: string;
  patient_id: string;
  patient_name: string;
  caregiver_id: string | null;
  dose_id: string | null;
  medication_name: string | null;
  direction: CallDirection;
  call_type: CallType;
  call_reason: CallReason | null;
  status: CallStatus;
  intent: CallIntent;
  transcript: string | null;
  created_at: string;
  updated_at: string;
}

export interface TimelineEvent {
  id: string;
  patient_id: string;
  call_id: string | null;
  event_type: string;
  title: string;
  description: string | null;
  occurred_at: string;
}

export interface ResponseBreakdown {
  confirmed_taken_pct: number;
  not_taken_pct: number;
  no_answer_pct: number;
  skipped_pct: number;
}

export interface DashboardStats {
  patient_id: string;
  period_days: number;
  resolved_dose_count: number;
  confirmed_pct: number;
  missed_or_no_answer_count: number;
  upcoming_appointments_count: number;
  next_appointment_at: string | null;
  next_appointment_doctor: string | null;
  breakdown: ResponseBreakdown;
}
