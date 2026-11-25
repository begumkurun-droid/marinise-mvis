export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const TOKEN_KEY = "marinise_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    if (res.status === 401) clearToken();
    const text = await res.text();
    throw new ApiError(res.status, text || res.statusText);
  }
  return (await res.json()) as T;
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const res = await fetch(`${API_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new ApiError(res.status, "Giriş başarısız");
  const data = (await res.json()) as { access_token: string };
  setToken(data.access_token);
  return data.access_token;
}

// --- Domain types (mirrors backend/app/schemas.py) ---
export type VesselPosition = {
  latitude: number;
  longitude: number;
  speed_over_ground_kn: number | null;
  course_over_ground_deg: number | null;
  heading_deg: number | null;
  navigational_status: string;
  received_at: string;
};

export type VesselListItem = {
  id: number;
  imo_number: string | null;
  mmsi: string | null;
  name: string;
  vessel_type: string;
  flag: string | null;
  length_m: number | null;
  last_position: VesselPosition | null;
};

export type VesselEngine = {
  category: string;
  manufacturer_name: string | null;
  engine_model_raw: string | null;
  rated_power_kw: number | null;
  rpm: number | null;
  quantity: number;
  verification_status: string;
  confidence_score: number;
};

export type CompanyInfo = {
  id: number;
  name: string;
  role: string | null;
  country: string | null;
  website: string | null;
  general_email: string | null;
};

export type ResearchLinks = {
  imo_number: string | null;
  mmsi: string | null;
  vessel_name: string;
  equasis_url: string;
  imo_gisis_url: string;
  note: string;
};

export type CompanyLinkInput = {
  company_name: string;
  role: string;
  country?: string;
  website?: string;
  general_email?: string;
  technical_email?: string;
  purchasing_email?: string;
  operations_email?: string;
  phone?: string;
  linkedin_url?: string;
  data_source?: string;
};

export type ResearchQueueItem = {
  id: number;
  name: string;
  imo_number: string | null;
  mmsi: string | null;
  vessel_type: string;
  customer_status: string | null;
};

// Section 7 - sol menüdeki rol listesiyle birebir.
export const COMPANY_ROLES: { value: string; label: string }[] = [
  { value: "registered_owner", label: "Registered Owner" },
  { value: "beneficial_owner", label: "Beneficial Owner" },
  { value: "shipowner", label: "Shipowner" },
  { value: "yacht_owner", label: "Yacht Owner" },
  { value: "technical_manager", label: "Technical Manager" },
  { value: "commercial_manager", label: "Commercial Manager" },
  { value: "ism_manager", label: "ISM Manager" },
  { value: "yacht_management", label: "Yacht Management" },
  { value: "fleet_operator", label: "Fleet Operator" },
  { value: "charter_management", label: "Charter Management" },
  { value: "ship_agent", label: "Ship Agent" },
  { value: "fleet_management", label: "Fleet Management" },
];

export type VesselDetail = VesselListItem & {
  call_sign: string | null;
  beam_m: number | null;
  draft_m: number | null;
  gross_tonnage: number | null;
  year_of_build: number | null;
  shipyard: string | null;
  departure_port: string | null;
  destination_port: string | null;
  eta: string | null;
  engines: VesselEngine[];
  companies: CompanyInfo[];
  lead_score: number | null;
  lead_priority: string | null;
  customer_status: string | null;
};

export type DashboardSummary = {
  active_tracked_vessels: number;
  vessels_in_turkey: number;
  vessels_approaching_turkey: number;
  cat_engine_vessels: number;
  mase_generator_vessels: number;
  new_leads_last_7_days: number;
  high_priority_leads: number;
  data_verification_rate_pct: number;
  contact_info_found_rate_pct: number;
};

export const getLiveMap = () => apiFetch<VesselListItem[]>("/vessels/map/live");
export const getDashboardSummary = () => apiFetch<DashboardSummary>("/dashboard/summary");
export const getVessel = (id: number) => apiFetch<VesselDetail>(`/vessels/${id}`);
export const listVessels = (query: string) => apiFetch<VesselListItem[]>(`/vessels${query}`);

export const getResearchLinks = (vesselId: number) =>
  apiFetch<ResearchLinks>(`/vessels/${vesselId}/research-links`);

export const addCompanyLink = (vesselId: number, payload: CompanyLinkInput) =>
  apiFetch<CompanyInfo>(`/vessels/${vesselId}/companies`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getResearchQueue = () => apiFetch<ResearchQueueItem[]>("/vessels/research/queue");
export const listCompanies = (query: string) => apiFetch<CompanyInfo[]>(`/companies${query}`);
