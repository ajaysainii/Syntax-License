"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { clearToken } from "@/app/components/AuthGuard";

const links = [
  { href: "/licenses", label: "Licenses" },
  { href: "/users", label: "Users" },
  { href: "/admins", label: "Admins" },
  { href: "/customers", label: "Customers" },
  { href: "/audit", label: "Audit Log" }
] satisfies Array<{ href: Route; label: string }>;

export function DashboardShell({
  children,
  title,
  subtitle
}: {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto flex min-h-screen w-full max-w-[1600px]">
        <aside className="hidden w-64 shrink-0 border-r border-gray-200 bg-white lg:flex lg:flex-col">
          <div className="border-b border-gray-200 px-6 py-5">
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-blue-600">Syntax Nation</div>
            <div className="mt-2 text-lg font-semibold text-gray-900">Licensing Admin</div>
            <p className="mt-1 text-sm text-gray-500">Standard admin workspace for licensing operations.</p>
          </div>
          <nav className="flex-1 space-y-1 px-4 py-4">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={
                  pathname === link.href
                    ? "block rounded-lg bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700"
                    : "block rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                }
              >
                {link.label}
              </Link>
            ))}
          </nav>
          <div className="border-t border-gray-200 px-6 py-4">
            <div className="text-xs font-medium uppercase tracking-wide text-gray-400">Target</div>
            <div className="mt-1 text-sm font-medium text-gray-700">lcs.syntaxnation.com</div>
          </div>
        </aside>
        <main className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 border-b border-gray-200 bg-white/95 backdrop-blur">
            <div className="flex items-center justify-between gap-4 px-4 py-4 sm:px-6">
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
                <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
              </div>
              <button
                className="inline-flex items-center rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                onClick={() => {
                  clearToken();
                  router.replace("/login");
                }}
              >
                Sign out
              </button>
            </div>
          </header>
          <div className="p-4 sm:p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
