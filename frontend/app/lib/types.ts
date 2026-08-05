export type Customer = {
  id: string;
  name: string;
  email: string;
  company?: string | null;
  notes?: string | null;
  created_at: string;
};

export type User = {
  id: string;
  customer_id: string;
  full_name: string;
  email: string;
  role: string;
  created_at: string;
};

export type License = {
  id: string;
  issued_to: string;
  email: string;
  plan: string;
  expires_at?: string | null;
  features: string[];
  status: string;
  product: string;
  key_prefix: string;
  created_at: string;
};

export type AuditLog = {
  id: string;
  actor_type: string;
  actor_id?: string | null;
  action: string;
  entity_type: string;
  entity_id?: string | null;
  changes: Record<string, unknown>;
  created_at: string;
};

export type Admin = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
};
