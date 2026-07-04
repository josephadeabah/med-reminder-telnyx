import type { CallReason, CallStatus, DoseStatus } from "./types";

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function formatRelative(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const seconds = Math.round(diffMs / 1000);
  if (Math.abs(seconds) < 60) return "just now";
  const minutes = Math.round(seconds / 60);
  if (Math.abs(minutes) < 60) return seconds > 0 ? `${minutes}m ago` : `in ${-minutes}m`;
  const hours = Math.round(minutes / 60);
  if (Math.abs(hours) < 24) return seconds > 0 ? `${hours}h ago` : `in ${-hours}h`;
  const days = Math.round(hours / 24);
  return seconds > 0 ? `${days}d ago` : `in ${days === 0 ? 1 : -days}d`;
}

export function callReasonLabel(reason: CallReason | null): string {
  const map: Record<string, string> = {
    medication_check: "Medication check",
    wellbeing_check: "Wellbeing check-in",
    appointment_reminder: "Appointment reminder",
    general_check: "General check-in",
    urgent_concern: "Urgent concern",
  };
  return reason ? map[reason] ?? reason : "No reason given";
}

const DOSE_STATUS_STYLES: Record<string, { label: string; dot: string; text: string }> = {
  pending: { label: "Pending", dot: "bg-muted", text: "text-muted" },
  confirmed: { label: "Taken", dot: "bg-accent", text: "text-accent" },
  missed: { label: "Missed", dot: "bg-clay", text: "text-clay" },
  skipped: { label: "Skipped", dot: "bg-muted", text: "text-muted" },
  escalated: { label: "No answer — escalated", dot: "bg-clay", text: "text-clay" },
};

export function doseStatusStyle(status: DoseStatus) {
  return DOSE_STATUS_STYLES[status] ?? { label: status, dot: "bg-muted", text: "text-muted" };
}

const CALL_STATUS_STYLES: Record<string, { label: string; dot: string; text: string; pulsing?: boolean }> = {
  queued: { label: "Queued", dot: "bg-amber", text: "text-amber", pulsing: true },
  initiated: { label: "Dialing", dot: "bg-amber", text: "text-amber", pulsing: true },
  ringing: { label: "Ringing", dot: "bg-amber", text: "text-amber", pulsing: true },
  answered: { label: "Live", dot: "bg-amber", text: "text-amber", pulsing: true },
  bridged: { label: "Live", dot: "bg-amber", text: "text-amber", pulsing: true },
  completed: { label: "Done", dot: "bg-accent", text: "text-accent" },
  failed: { label: "Failed", dot: "bg-clay", text: "text-clay" },
  busy: { label: "Busy", dot: "bg-clay", text: "text-clay" },
  "no-answer": { label: "No answer", dot: "bg-clay", text: "text-clay" },
};

export function callStatusStyle(status: CallStatus) {
  return CALL_STATUS_STYLES[status] ?? { label: status, dot: "bg-muted", text: "text-muted" };
}
