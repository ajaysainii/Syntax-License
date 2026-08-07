"use client";

import { FormEvent, useEffect, useState } from "react";

import { DashboardShell } from "@/app/components/DashboardShell";
import { getStoredToken } from "@/app/components/AuthGuard";
import { api } from "@/app/lib/api";
import type { Admin, AuditLog, Customer, License, User } from "@/app/lib/types";

type ResourceKind = "customers" | "users" | "licenses" | "audit" | "admins";

export function ResourcePage({ kind }: { kind: ResourceKind }) {
  const [token, setToken] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Array<Customer | User | License | AuditLog | Admin>>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [licenseKey, setLicenseKey] = useState<string | null>(null);
  const [revealedLicenseKeys, setRevealedLicenseKeys] = useState<Record<string, string>>({});
  const [revealingLicenseId, setRevealingLicenseId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [licenseModalOpen, setLicenseModalOpen] = useState(false);
  const [customerModalOpen, setCustomerModalOpen] = useState(false);
  const [userModalOpen, setUserModalOpen] = useState(false);
  const [adminModalOpen, setAdminModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedAdmin, setSelectedAdmin] = useState<Admin | null>(null);

  useEffect(() => {
    setToken(getStoredToken());
  }, []);

  async function load() {
    if (!token) return;
    setError(null);
    try {
      if (kind === "customers") {
        const response = await api.customers(token, query);
        setItems(response.items as Customer[]);
      } else if (kind === "users") {
        const response = await api.users(token, query);
        setItems(response.items as User[]);
        const customerResponse = await api.customers(token);
        setCustomers(customerResponse.items as Customer[]);
      } else if (kind === "licenses") {
        const response = await api.licenses(token, query, status);
        setItems(response.items as License[]);
        const userResponse = await api.users(token);
        setUsers(userResponse.items as User[]);
      } else if (kind === "admins") {
        const response = await api.admins(token);
        const adminItems = response.items as Admin[];
        setItems(adminItems);
        setAdmins(adminItems);
      } else {
        const response = await api.auditLogs(token);
        setItems(response.items as AuditLog[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    }
  }

  useEffect(() => {
    void load();
  }, [token, kind]);

  async function onCreateCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const form = new FormData(event.currentTarget);
    await api.createCustomer(token, {
      name: form.get("name"),
      email: form.get("email"),
      company: form.get("company"),
      notes: form.get("notes")
    });
    event.currentTarget.reset();
    setCustomerModalOpen(false);
    await load();
  }

  async function onCreateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const form = new FormData(event.currentTarget);
    await api.createUser(token, {
      customer_id: form.get("customer_id"),
      full_name: form.get("full_name"),
      email: form.get("email"),
      role: form.get("role")
    });
    event.currentTarget.reset();
    setUserModalOpen(false);
    await load();
  }

  async function onCreateLicense(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const form = new FormData(event.currentTarget);
    const response = await api.createLicense(token, {
      user_id: form.get("user_id"),
      product: form.get("product"),
      plan: form.get("plan"),
      expires_at: form.get("expires_at") || null,
      features: String(form.get("features") ?? "")
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean)
    });
    setLicenseKey(response.license_key);
    event.currentTarget.reset();
    setLicenseModalOpen(false);
    await load();
  }

  async function revealLicenseKey(id: string) {
    if (!token) return;
    if (revealedLicenseKeys[id]) return;
    setRevealingLicenseId(id);
    try {
      const response = await api.getLicenseKey(token, id);
      setRevealedLicenseKeys((current) => ({ ...current, [id]: response.license_key }));
    } finally {
      setRevealingLicenseId(null);
    }
  }

  async function updateLicense(id: string, action: "suspend" | "revoke" | "reactivate") {
    if (!token) return;
    await api.changeLicenseStatus(token, id, { action });
    await load();
  }

  async function onUpdateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedUser) return;
    const form = new FormData(event.currentTarget);
    await api.updateUser(token, selectedUser.id, {
      customer_id: form.get("customer_id"),
      full_name: form.get("full_name"),
      email: form.get("email"),
      role: form.get("role")
    });
    setUserModalOpen(false);
    setSelectedUser(null);
    await load();
  }

  async function onUpdateAdmin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedAdmin) return;
    const form = new FormData(event.currentTarget);
    await api.updateAdmin(token, selectedAdmin.id, {
      email: form.get("email"),
      full_name: form.get("full_name"),
      is_active: form.get("is_active") === "on",
      password: form.get("password") || null
    });
    setAdminModalOpen(false);
    setSelectedAdmin(null);
    await load();
  }

  const metrics =
    kind === "licenses"
      ? [
          { label: "Licenses", value: String(items.length) },
          { label: "Active", value: String(items.filter((item) => (item as License).status === "active").length) },
          { label: "Filtered", value: query || "All" }
        ]
      : kind === "users"
        ? [
            { label: "Users", value: String(items.length) },
            { label: "Customers", value: String(customers.length) },
            { label: "Filtered", value: query || "All" }
          ]
          : kind === "customers"
          ? [
              { label: "Customers", value: String(items.length) },
              { label: "Domain", value: "Syntax" },
              { label: "Filtered", value: query || "All" }
            ]
          : kind === "admins"
            ? [
                { label: "Admins", value: String(admins.length) },
                { label: "Active", value: String(admins.filter((item) => item.is_active).length) },
                { label: "Mode", value: "Manage" }
              ]
          : [
              { label: "Audit Rows", value: String(items.length) },
              { label: "Source", value: "Admin + API" },
              { label: "Mode", value: "Read only" }
            ];

  const titleMap = {
    licenses: "License Management",
    users: "Users",
    admins: "Admins",
    customers: "Customers",
    audit: "Audit Log"
  } as const;

  const subtitleMap = {
    licenses: "Create and manage product licenses for Syntax desktop and CLI customers.",
    users: "Manage licensed users under each customer account.",
    admins: "Manage admin accounts and update operator access.",
    customers: "Track customer accounts and account-level ownership.",
    audit: "Review system and admin activity."
  } as const;

  return (
    <DashboardShell title={titleMap[kind]} subtitle={subtitleMap[kind]}>
      <section className="grid gap-4 md:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="text-xs font-medium uppercase tracking-wide text-gray-500">{metric.label}</div>
            <div className="mt-2 text-2xl font-semibold text-gray-900">{metric.value}</div>
          </div>
        ))}
      </section>

      {kind !== "audit" ? (
        <section className="mt-6">
          <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
            <div className="flex flex-col gap-3 border-b border-gray-200 p-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-base font-semibold text-gray-900">{titleMap[kind]}</h2>
                <p className="mt-1 text-sm text-gray-500">Search, review, and manage records.</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  className="h-10 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-900 outline-none placeholder:text-gray-400 focus:border-blue-500"
                  placeholder={`Search ${kind}`}
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
                {kind === "licenses" ? (
                  <select
                    className="h-10 rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500"
                    value={status}
                    onChange={(event) => setStatus(event.target.value)}
                  >
                    <option value="">All statuses</option>
                    <option value="active">Active</option>
                    <option value="suspended">Suspended</option>
                    <option value="revoked">Revoked</option>
                  </select>
                ) : null}
                {kind === "licenses" ? (
                  <button
                    className="inline-flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700"
                    onClick={() => setLicenseModalOpen(true)}
                  >
                    Add License
                  </button>
                ) : null}
                {kind === "customers" ? (
                  <button
                    className="inline-flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700"
                    onClick={() => setCustomerModalOpen(true)}
                  >
                    Add Customer
                  </button>
                ) : null}
                {kind === "users" ? (
                  <button
                    className="inline-flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700"
                    onClick={() => setUserModalOpen(true)}
                  >
                    Add User
                  </button>
                ) : null}
                <button
                  className="inline-flex h-10 items-center rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  onClick={() => void load()}
                >
                  Refresh
                </button>
              </div>
            </div>
            {error ? <div className="border-b border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div> : null}
            {kind === "licenses" && licenseKey ? (
              <div className="border-b border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                New license issued: <span className="font-mono">{licenseKey}</span>
              </div>
            ) : null}
            <div className="overflow-x-auto">
              {kind === "customers" ? <CustomersTable rows={items as Customer[]} /> : null}
              {kind === "users" ? <UsersTable rows={items as User[]} onEdit={(user) => {
                setSelectedUser(user);
                setUserModalOpen(true);
              }} /> : null}
              {kind === "admins" ? <AdminsTable rows={admins} onEdit={(admin) => {
                setSelectedAdmin(admin);
                setAdminModalOpen(true);
              }} /> : null}
              {kind === "licenses" ? (
                <LicensesTable
                  rows={items as License[]}
                  onAction={updateLicense}
                  onReveal={revealLicenseKey}
                  revealedKeys={revealedLicenseKeys}
                  revealingLicenseId={revealingLicenseId}
                />
              ) : null}
            </div>
          </div>
        </section>
      ) : (
        <section className="mt-6 rounded-xl border border-gray-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-gray-200 p-4">
            <div>
              <h2 className="text-base font-semibold text-gray-900">Audit Timeline</h2>
              <p className="mt-1 text-sm text-gray-500">Recent administrative and validation activity.</p>
            </div>
            <button
              className="inline-flex h-10 items-center rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 hover:bg-gray-50"
              onClick={() => void load()}
            >
              Refresh
            </button>
          </div>
          <div className="overflow-x-auto">
            <AuditTable rows={items as AuditLog[]} />
          </div>
        </section>
      )}

      {kind === "licenses" && licenseModalOpen ? (
        <Modal
          title="Issue License"
          subtitle="Generate a new Syntax license and assign it to a user."
          onClose={() => {
            setLicenseModalOpen(false);
            setLicenseKey(null);
          }}
        >
          <LicenseForm
            users={users}
            onSubmit={async (event) => {
              await onCreateLicense(event);
            }}
          />
        </Modal>
      ) : null}
      {kind === "customers" && customerModalOpen ? (
        <Modal
          title="Add Customer"
          subtitle="Create a new customer account."
          onClose={() => setCustomerModalOpen(false)}
        >
          <CustomerForm onSubmit={onCreateCustomer} />
        </Modal>
      ) : null}
      {kind === "users" && userModalOpen && selectedUser ? (
        <Modal
          title="Edit User"
          subtitle="Update user details and account assignment."
          onClose={() => {
            setUserModalOpen(false);
            setSelectedUser(null);
          }}
        >
          <UserForm customers={customers} onSubmit={onUpdateUser} initial={selectedUser} submitLabel="Save Changes" />
        </Modal>
      ) : null}
      {kind === "users" && userModalOpen && !selectedUser ? (
        <Modal
          title="Add User"
          subtitle="Create a new user under an existing customer."
          onClose={() => setUserModalOpen(false)}
        >
          <UserForm customers={customers} onSubmit={onCreateUser} />
        </Modal>
      ) : null}
      {kind === "admins" && adminModalOpen && selectedAdmin ? (
        <Modal
          title="Edit Admin"
          subtitle="Update admin account details and optional password."
          onClose={() => {
            setAdminModalOpen(false);
            setSelectedAdmin(null);
          }}
        >
          <AdminForm admin={selectedAdmin} onSubmit={onUpdateAdmin} />
        </Modal>
      ) : null}
    </DashboardShell>
  );
}

function Modal({
  children,
  onClose,
  subtitle,
  title
}: {
  children: React.ReactNode;
  onClose: () => void;
  subtitle: string;
  title: string;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4" onClick={onClose}>
      <div className="w-full max-w-xl rounded-xl border border-gray-200 bg-white p-5 shadow-xl" onClick={(event) => event.stopPropagation()}>
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          </div>
          <button
            className="inline-flex h-9 items-center rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
            onClick={onClose}
            type="button"
          >
            Close
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function TableShell({ children }: { children: React.ReactNode }) {
  return <table className="min-w-full divide-y divide-gray-200 text-sm">{children}</table>;
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">{children}</th>;
}

function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`px-4 py-3 align-top text-sm text-gray-700 ${className}`}>{children}</td>;
}

function StatusBadge({ status }: { status: string }) {
  const styles =
    status === "active"
      ? "bg-green-50 text-green-700 ring-green-600/20"
      : status === "suspended"
        ? "bg-yellow-50 text-yellow-700 ring-yellow-600/20"
        : "bg-red-50 text-red-700 ring-red-600/20";
  return <span className={`inline-flex rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${styles}`}>{status}</span>;
}

function CustomersTable({ rows }: { rows: Customer[] }) {
  return (
    <TableShell>
      <thead className="bg-gray-50">
        <tr><Th>Customer</Th><Th>Email</Th><Th>Company</Th></tr>
      </thead>
      <tbody className="divide-y divide-gray-200 bg-white">
        {rows.map((row) => (
          <tr key={row.id}>
            <Td><div className="font-medium text-gray-900">{row.name}</div></Td>
            <Td>{row.email}</Td>
            <Td>{row.company ?? "Individual"}</Td>
          </tr>
        ))}
      </tbody>
    </TableShell>
  );
}

function UsersTable({ rows, onEdit }: { rows: User[]; onEdit: (user: User) => void }) {
  return (
    <TableShell>
      <thead className="bg-gray-50">
        <tr><Th>User</Th><Th>Email</Th><Th>Role</Th><Th>Actions</Th></tr>
      </thead>
      <tbody className="divide-y divide-gray-200 bg-white">
        {rows.map((row) => (
          <tr key={row.id}>
            <Td><div className="font-medium text-gray-900">{row.full_name}</div></Td>
            <Td>{row.email}</Td>
            <Td>{row.role}</Td>
            <Td>
              <button
                className="inline-flex h-8 items-center rounded-lg border border-gray-300 bg-white px-3 text-xs font-medium text-gray-700 hover:bg-gray-50"
                onClick={() => onEdit(row)}
              >
                Edit
              </button>
            </Td>
          </tr>
        ))}
      </tbody>
    </TableShell>
  );
}

function AdminsTable({ rows, onEdit }: { rows: Admin[]; onEdit: (admin: Admin) => void }) {
  return (
    <TableShell>
      <thead className="bg-gray-50">
        <tr><Th>Name</Th><Th>Email</Th><Th>Status</Th><Th>Actions</Th></tr>
      </thead>
      <tbody className="divide-y divide-gray-200 bg-white">
        {rows.map((row) => (
          <tr key={row.id}>
            <Td><div className="font-medium text-gray-900">{row.full_name}</div></Td>
            <Td>{row.email}</Td>
            <Td><StatusBadge status={row.is_active ? "active" : "revoked"} /></Td>
            <Td>
              <button
                className="inline-flex h-8 items-center rounded-lg border border-gray-300 bg-white px-3 text-xs font-medium text-gray-700 hover:bg-gray-50"
                onClick={() => onEdit(row)}
              >
                Edit
              </button>
            </Td>
          </tr>
        ))}
      </tbody>
    </TableShell>
  );
}

function LicensesTable({
  rows,
  onAction,
  onReveal,
  revealedKeys,
  revealingLicenseId
}: {
  rows: License[];
  onAction: (id: string, action: "suspend" | "revoke" | "reactivate") => Promise<void>;
  onReveal: (id: string) => Promise<void>;
  revealedKeys: Record<string, string>;
  revealingLicenseId: string | null;
}) {
  return (
    <TableShell>
      <thead className="bg-gray-50">
        <tr><Th>Issued To</Th><Th>Product</Th><Th>Plan</Th><Th>Status</Th><Th>Key Prefix</Th><Th>Actions</Th></tr>
      </thead>
      <tbody className="divide-y divide-gray-200 bg-white">
        {rows.map((row) => (
          <tr key={row.id}>
            <Td>
              <div className="font-medium text-gray-900">{row.issued_to}</div>
              <div className="mt-1 text-xs text-gray-500">{row.email}</div>
            </Td>
            <Td>{row.product}</Td>
            <Td>
              <div className="font-medium text-gray-900">{row.plan}</div>
              <div className="mt-1 text-xs text-gray-500">{row.features.join(", ") || "No features"}</div>
            </Td>
            <Td><StatusBadge status={row.status} /></Td>
            <Td className="font-mono text-xs">
              <div className="flex items-center gap-2">
                <span>{revealedKeys[row.id] ?? row.key_prefix}</span>
                <button
                  className="inline-flex h-7 items-center rounded-lg border border-gray-300 bg-white px-2 text-[11px] font-medium text-gray-700 hover:bg-gray-50"
                  onClick={() => void onReveal(row.id)}
                  type="button"
                >
                  {revealingLicenseId === row.id ? "..." : "Eye"}
                </button>
              </div>
            </Td>
            <Td className="whitespace-nowrap">
              {row.status === "active" ? (
                <button
                  className="mr-2 inline-flex h-8 items-center rounded-lg border border-gray-300 bg-white px-3 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  onClick={() => void onAction(row.id, "suspend")}
                >
                  Suspend
                </button>
              ) : (
                <button
                  className="mr-2 inline-flex h-8 items-center rounded-lg border border-gray-300 bg-white px-3 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  onClick={() => void onAction(row.id, "reactivate")}
                >
                  Reactivate
                </button>
              )}
              <button
                className="inline-flex h-8 items-center rounded-lg border border-red-200 bg-red-50 px-3 text-xs font-medium text-red-700 hover:bg-red-100"
                onClick={() => void onAction(row.id, "revoke")}
              >
                Revoke
              </button>
            </Td>
          </tr>
        ))}
      </tbody>
    </TableShell>
  );
}

function AuditTable({ rows }: { rows: AuditLog[] }) {
  return (
    <TableShell>
      <thead className="bg-gray-50">
        <tr><Th>Action</Th><Th>Actor</Th><Th>Entity</Th><Th>Timestamp</Th></tr>
      </thead>
      <tbody className="divide-y divide-gray-200 bg-white">
        {rows.map((row) => (
          <tr key={row.id}>
            <Td>
              <div className="font-medium text-gray-900">{row.action}</div>
              <div className="mt-1 text-xs text-gray-500">{JSON.stringify(row.changes)}</div>
            </Td>
            <Td>{row.actor_type}</Td>
            <Td>{row.entity_type}</Td>
            <Td>{new Date(row.created_at).toLocaleString()}</Td>
          </tr>
        ))}
      </tbody>
    </TableShell>
  );
}

function CustomerForm({ onSubmit }: { onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void> }) {
  return (
    <form className="space-y-3" onSubmit={(event) => void onSubmit(event)}>
      <Field label="Customer name"><input name="name" placeholder="Northwind Studio" required /></Field>
      <Field label="Email"><input name="email" placeholder="ops@northwind.test" type="email" required /></Field>
      <Field label="Company"><input name="company" placeholder="Northwind" /></Field>
      <Field label="Notes"><textarea name="notes" placeholder="Optional notes" rows={4} /></Field>
      <PrimaryButton text="Save Customer" />
    </form>
  );
}

function UserForm({
  customers,
  initial,
  submitLabel,
  onSubmit
}: {
  customers: Customer[];
  initial?: User | null;
  submitLabel?: string;
  onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}) {
  return (
    <form className="space-y-3" onSubmit={(event) => void onSubmit(event)}>
      <Field label="Customer">
        <select defaultValue={initial?.customer_id ?? ""} name="customer_id" required>
          <option value="">Select customer</option>
          {customers.map((customer) => (
            <option key={customer.id} value={customer.id}>{customer.name}</option>
          ))}
        </select>
      </Field>
      <Field label="Full name"><input name="full_name" placeholder="Avery Cole" defaultValue={initial?.full_name ?? ""} required /></Field>
      <Field label="Email"><input name="email" placeholder="avery@northwind.test" defaultValue={initial?.email ?? ""} type="email" required /></Field>
      <Field label="Role"><input name="role" placeholder="owner" defaultValue={initial?.role ?? "owner"} /></Field>
      <PrimaryButton text={submitLabel ?? (initial ? "Save Changes" : "Save User")} />
    </form>
  );
}

function LicenseForm({
  users,
  onSubmit
}: {
  users: User[];
  onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}) {
  return (
    <form
      className="space-y-3"
      onSubmit={(event) => void onSubmit(event)}
    >
      <Field label="User">
        <select name="user_id" required>
          <option value="">Select user</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>{user.full_name} · {user.email}</option>
          ))}
        </select>
      </Field>
      <Field label="Product">
        <select defaultValue="syntax" name="product" required>
          <option value="syntax">Syntax</option>
          <option value="syntax-cli">Syntax CLI (alias)</option>
          <option value="syntax-desktop">Syntax Desktop (alias)</option>
        </select>
      </Field>
      <Field label="Plan"><input name="plan" placeholder="pro" required /></Field>
      <Field label="Expiry"><input name="expires_at" type="datetime-local" /></Field>
      <Field label="Features"><input name="features" placeholder="offline-cache, priority-support" /></Field>
      <PrimaryButton text="Issue License" />
    </form>
  );
}

function Field({ children, label }: { children: React.ReactNode; label: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-gray-700">{label}</span>
      <div className="[&>input]:block [&>input]:h-10 [&>input]:w-full [&>input]:rounded-lg [&>input]:border [&>input]:border-gray-300 [&>input]:bg-white [&>input]:px-3 [&>input]:text-sm [&>input]:text-gray-900 [&>input]:outline-none [&>input]:focus:border-blue-500 [&>select]:block [&>select]:h-10 [&>select]:w-full [&>select]:rounded-lg [&>select]:border [&>select]:border-gray-300 [&>select]:bg-white [&>select]:px-3 [&>select]:text-sm [&>select]:text-gray-900 [&>select]:outline-none [&>select]:focus:border-blue-500 [&>textarea]:block [&>textarea]:w-full [&>textarea]:rounded-lg [&>textarea]:border [&>textarea]:border-gray-300 [&>textarea]:bg-white [&>textarea]:px-3 [&>textarea]:py-2.5 [&>textarea]:text-sm [&>textarea]:text-gray-900 [&>textarea]:outline-none [&>textarea]:focus:border-blue-500">
        {children}
      </div>
    </label>
  );
}

function PrimaryButton({ text }: { text: string }) {
  return (
    <button className="inline-flex h-10 items-center justify-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700" type="submit">
      {text}
    </button>
  );
}

function AdminForm({ admin, onSubmit }: { admin: Admin; onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void> }) {
  return (
    <form className="space-y-3" onSubmit={(event) => void onSubmit(event)}>
      <Field label="Full name"><input name="full_name" defaultValue={admin.full_name} required /></Field>
      <Field label="Email"><input name="email" defaultValue={admin.email} type="email" required /></Field>
      <Field label="Password"><input name="password" placeholder="Leave blank to keep current password" type="password" /></Field>
      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input className="h-4 w-4 rounded border-gray-300" defaultChecked={admin.is_active} name="is_active" type="checkbox" />
        Active admin
      </label>
      <PrimaryButton text="Save Admin" />
    </form>
  );
}
