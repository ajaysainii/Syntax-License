"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

const TOKEN_KEY = "syntax_admin_token";

export function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token && pathname !== "/login") {
      router.replace("/login");
      return;
    }
    if (token && pathname === "/login") {
      router.replace("/licenses");
      return;
    }
    setReady(true);
  }, [pathname, router]);

  if (!ready) {
    return null;
  }

  return <>{children}</>;
}

