import type {
  CallDetail,
  CallReason,
  CallSummary,
  CallType,
  Caregiver,
  DashboardStats,
  DoseWithCall,
  HealthSnapshot,
  Patient,
  TimelineEvent,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_TOKEN = process.env.NEXT_PUBLIC_API_TOKEN;

function headers(): HeadersInit {
  const h: HeadersInit = { "Content-Type": "application/json" };
  if (API_TOKEN) h["Authorization"] = `Bearer ${API_TOKEN}`;
  return h;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // not JSON - keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

function get<T>(path: string): Promise<T> {
  return fetch(`${API_URL}${path}`, { headers: headers(), cache: "no-store" }).then(handle<T>);
}

function post<T>(path: string, body?: unknown): Promise<T> {
  return fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: headers(),
    body: body ? JSON.stringify(body) : undefined,
  }).then(handle<T>);
}

// --- Patients & caregivers ---
// lib/api.ts
export const listPatients = () => {
  console.log("Fetching patients...");
  return get<Patient[]>("/patients").then((patients) => {
    console.log("Patients fetched:", patients);
    return patients;
  });
};

export const getCurrentCaregiver = () => {
  console.log("Fetching current caregiver...");
  return get<Caregiver>("/caregivers/me").then((caregiver) => {
    console.log("Caregiver fetched:", caregiver);
    return caregiver;
  });
};
export const getPatient = (id: string) => get<Patient>(`/patients/${id}`);
export const getHealthSnapshot = (patientId: string) => get<HealthSnapshot>(`/patients/${patientId}/snapshot`);

// --- Medications / doses ---
export const listTodaysDoses = (patientId: string, on?: string) =>
  get<DoseWithCall[]>(`/patients/${patientId}/doses${on ? `?on=${on}` : ""}`);

// --- Timeline ---
export const listTimeline = (patientId: string, limit = 20) =>
  get<TimelineEvent[]>(`/patients/${patientId}/timeline?limit=${limit}`);

// --- Calls ---
export const listCalls = (params: { patientId?: string; direction?: string; limit?: number } = {}) => {
  const qs = new URLSearchParams();
  if (params.patientId) qs.set("patient_id", params.patientId);
  if (params.direction) qs.set("direction", params.direction);
  if (params.limit) qs.set("limit", String(params.limit));
  return get<CallSummary[]>(`/calls${qs.toString() ? `?${qs}` : ""}`);
};

export const listLiveCalls = (patientId?: string) =>
  get<CallSummary[]>(`/calls/live${patientId ? `?patient_id=${patientId}` : ""}`);

export const getCall = (id: string) => get<CallDetail>(`/calls/${id}`);

export const placeCaregiverCall = (payload: {
  patient_id: string;
  caregiver_id: string;
  call_type: CallType;
  call_reason?: CallReason | null;
  pre_call_note?: string | null;
}) => {
  console.log("Sending caregiver call payload:", payload);
  return post<CallDetail>("/calls/caregiver", payload);
};

export const triggerSystemCall = (doseId: string) => post<CallDetail>("/calls/system", { dose_id: doseId });

export const endCall = (id: string) => post<CallDetail>(`/calls/${id}/end`);

// --- Dashboard ---
export const getDashboardStats = (patientId: string, days = 30) =>
  get<DashboardStats>(`/dashboard/stats?patient_id=${patientId}&days=${days}`);