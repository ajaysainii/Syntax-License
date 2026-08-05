import { AuthGuard } from "@/app/components/AuthGuard";
import { LoginForm } from "@/app/components/LoginForm";

export default function LoginPage() {
  return (
    <AuthGuard>
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <div className="grid w-full max-w-5xl gap-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-xl bg-gray-900 p-6 text-white">
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-300">Syntax Nation</div>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight">Licensing Control Surface</h1>
            <p className="mt-3 max-w-md text-sm leading-6 text-gray-300">
              Manage customers, users, license keys, device activations, and audit history from one admin workspace.
            </p>
            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-white/10 bg-white/5 p-4">
                <div className="text-xs uppercase tracking-wide text-gray-400">Domain</div>
                <div className="mt-1 text-sm font-medium">lcs.syntaxnation.com</div>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-4">
                <div className="text-xs uppercase tracking-wide text-gray-400">Access</div>
                <div className="mt-1 text-sm font-medium">Admin only</div>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-2xl font-semibold text-gray-900">Sign in</h2>
            <p className="mt-2 text-sm text-gray-500">Use the seeded admin account or your deployed operator credentials.</p>
            <div className="mt-6">
              <LoginForm />
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
