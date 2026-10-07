export type RecruitmentPost = {
  id: string;
  title: string;
  department: string | null;
  job_family: string | null;
  location_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_text: string | null;
  vacancies: number | null;
  description: string | null;
};

export type SourceDocument = {
  id: string;
  title: string;
  url: string;
  document_type: string;
  version_number: number;
  published_at: string | null;
  page: number | null;
  section: string | null;
  verification_status?: string;
};

export type EvidenceFragment = {
  id: string;
  source_document_id: string;
  source_title: string;
  url: string;
  page_number: number | null;
  section_heading: string | null;
  text_content: string;
};

export type Recruitment = {
  id: string;
  organization_id: string;
  organization_name?: string | null;
  title: string;
  slug: string;
  recruitment_type: string;
  status: string;
  published_at: string | null;
  last_verified_at: string | null;
  application_start_date: string | null;
  application_deadline: string | null;
  exam_date: string | null;
  official_apply_url: string | null;
  required_education_level: string | null;
  verification_status: string;
  posts: RecruitmentPost[];
  official_sources: SourceDocument[];
};

export type CandidateProfile = {
  user_id?: string;
  date_of_birth: string | null;
  gender: string;
  category: string;
  domicile_state: string;
  preferred_states: string[];
  education_level: string;
  degree_name: string;
  specialization: string;
  experience_years: number;
};

export type EvaluationRuleReason = {
  rule_type: string;
  status: 'PASS' | 'CHECK_FAILED' | 'NEEDS_VERIFICATION' | 'INSUFFICIENT_DATA';
  evidence_id: string | null;
  page?: number | null;
  section?: string | null;
  source_quote?: string | null;
  message: string;
};

export type EvaluationResult = {
  result: 'ELIGIBLE' | 'LIKELY_ELIGIBLE' | 'NEEDS_VERIFICATION' | 'NOT_ELIGIBLE' | 'INSUFFICIENT_DATA';
  engine_version: string;
  reasons: EvaluationRuleReason[];
};

export type ProfileEvaluationItem = {
  recruitment_id: string;
  recruitment_title: string;
  job_post_id: string;
  job_post_title: string;
  result: string;
  engine_version: string;
  reasons: EvaluationRuleReason[];
};

export type ReminderItem = {
  id: string;
  user_id: string;
  recruitment_id: string;
  event_type: string;
  scheduled_for: string;
};

export type AssistantCitation = {
  document_id: string;
  document_title?: string | null;
  url?: string | null;
  page?: number | null;
  section?: string | null;
  quote?: string | null;
};

export type AssistantResponse = {
  answer: string;
  citations: AssistantCitation[];
  verification_status: string;
  last_verified_at: string | null;
};

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '');

export async function apiGet<T>(path: string): Promise<
  | { ok: true; data: T }
  | { ok: false; error: string; status?: number }
> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { cache: 'no-store' });
    if (!response.ok) {
      return { ok: false, error: `The API returned HTTP ${response.status}.`, status: response.status };
    }
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return { ok: false, error: `Could not connect to the API at ${API_BASE_URL}.` };
  }
}

export async function apiPost<T>(path: string, body: unknown): Promise<
  | { ok: true; data: T }
  | { ok: false; error: string; status?: number }
> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) {
      return { ok: false, error: data.detail ?? `API error ${response.status}`, status: response.status };
    }
    return { ok: true, data: data as T };
  } catch {
    return { ok: false, error: `Could not connect to the API at ${API_BASE_URL}.` };
  }
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}
