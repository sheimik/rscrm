export interface PageResponse<T> {
  items: T[];
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface ApiCity {
  id: string;
  name: string;
}

export interface ApiDistrict {
  id: string;
  name: string;
}

export interface ApiUserSummary {
  id: string;
  full_name: string;
}

export interface ApiUser extends ApiUserSummary {
  email: string;
  phone?: string | null;
  role: string;
  city_id?: string | null;
  district_id?: string | null;
  is_active: boolean;
  last_login_at?: string | null;
  city?: ApiCity | null;
  district?: ApiDistrict | null;
  created_at?: string;
  updated_at?: string;
  scopes?: string[] | null;
}

export interface UserCreatePayload {
  email: string;
  password: string;
  full_name: string;
  phone?: string | null;
  role: string;
  city_id?: string | null;
  district_id?: string | null;
  is_active?: boolean;
}

export interface UserUpdatePayload {
  email?: string;
  full_name?: string;
  phone?: string | null;
  role?: string;
  city_id?: string | null;
  district_id?: string | null;
  is_active?: boolean;
  password?: string;
}

export interface ApiObject {
  id: string;
  type: string;
  address: string;
  city_id: string;
  district_id?: string | null;
  gps_lat?: number | null;
  gps_lng?: number | null;
  status: string;
  tags?: string[] | null;
  responsible_user_id?: string | null;
  responsible_user?: ApiUserSummary | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  visits_count?: number;
  last_visit_at?: string | null;
  created_by?: string;
  updated_by?: string | null;
  created_at?: string;
  updated_at?: string;
  version?: number;
  city?: ApiCity | null;
  district?: ApiDistrict | null;
}

export interface ObjectCreatePayload {
  type: string;
  address: string;
  city_id: string;
  district_id?: string | null;
  gps_lat?: number | null;
  gps_lng?: number | null;
  status?: string;
  tags?: string[];
  responsible_user_id?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
}

export interface ObjectUpdatePayload extends Partial<ObjectCreatePayload> {
  version?: number;
}

export interface ApiVisit {
  id: string;
  object_id: string;
  unit_id?: string | null;
  customer_id?: string | null;
  engineer_id: string;
  status: string;
  scheduled_at?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  interests?: string[] | null;
  outcome_text?: string | null;
  next_action_due_at?: string | null;
  version: number;
  created_at?: string;
  updated_at?: string;
  object?: ApiObject | null;
  customer?: ApiCustomer | null;
  engineer?: ApiUserSummary | null;
}

export interface ApiCustomer {
  id: string;
  object_id: string;
  unit_id?: string | null;
  full_name?: string | null;
  phone?: string | null;
  portrait_text?: string | null;
  current_provider?: string | null;
  provider_rating?: number | null;
  satisfied?: boolean | null;
  interests?: string[] | null;
  preferred_call_time?: string | null;
  desired_price?: string | null;
  notes?: string | null;
  gdpr_consent: boolean;
  last_interaction_at?: string | null;
  created_at?: string;
  updated_at?: string;
  object?: ApiObject | null;
}
