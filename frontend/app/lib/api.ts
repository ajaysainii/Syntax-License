const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; admin: { full_name: string; email: string } }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  me: (token: string) => request("/auth/me", {}, token),
  admins: (token: string) => request<{ items: unknown[]; total: number }>("/admins", {}, token),
  updateAdmin: (token: string, id: string, payload: unknown) =>
    request(`/admins/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token),
  customers: (token: string, q = "") =>
    request<{ items: unknown[]; total: number }>(`/customers${q ? `?q=${encodeURIComponent(q)}` : ""}`, {}, token),
  createCustomer: (token: string, payload: unknown) =>
    request("/customers", { method: "POST", body: JSON.stringify(payload) }, token),
  users: (token: string, q = "") =>
    request<{ items: unknown[]; total: number }>(`/users${q ? `?q=${encodeURIComponent(q)}` : ""}`, {}, token),
  createUser: (token: string, payload: unknown) =>
    request("/users", { method: "POST", body: JSON.stringify(payload) }, token),
  updateUser: (token: string, id: string, payload: unknown) =>
    request(`/users/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token),
  licenses: (token: string, q = "", status = "") =>
    request<{ items: unknown[]; total: number }>(
      `/licenses?${new URLSearchParams({
        ...(q ? { q } : {}),
        ...(status ? { status } : {})
      }).toString()}`,
      {},
      token
    ),
  createLicense: (token: string, payload: unknown) =>
    request<{ license_key: string; license: unknown }>("/licenses", { method: "POST", body: JSON.stringify(payload) }, token),
  changeLicenseStatus: (token: string, id: string, payload: unknown) =>
    request(`/licenses/${id}/actions`, { method: "POST", body: JSON.stringify(payload) }, token),
  auditLogs: (token: string) => request<{ items: unknown[] }>("/audit-logs", {}, token)
};
