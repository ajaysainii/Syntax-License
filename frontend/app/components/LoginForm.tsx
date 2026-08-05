"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { api } from "@/app/lib/api";
import { storeToken } from "@/app/components/AuthGuard";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await api.login(email, password);
      storeToken(response.access_token);
      router.replace("/licenses");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <label className="block">
        <span className="mb-1.5 block text-sm font-medium text-gray-700">Email</span>
        <input
          className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none ring-0 placeholder:text-gray-400 focus:border-blue-500"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Admin email"
        />
      </label>
      <label className="block">
        <span className="mb-1.5 block text-sm font-medium text-gray-700">Password</span>
        <input
          className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none ring-0 placeholder:text-gray-400 focus:border-blue-500"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Password"
          type="password"
        />
      </label>
      {error ? <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
      <button
        className="inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
        disabled={loading}
        type="submit"
      >
        {loading ? "Signing in..." : "Enter Control Surface"}
      </button>
    </form>
  );
}
