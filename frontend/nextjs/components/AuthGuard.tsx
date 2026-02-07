"use client";

import { useAuth } from "@/hooks/AuthContext";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

const PUBLIC_PATHS = ["/login"];

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, authEnabled } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isPublicPath = PUBLIC_PATHS.some((p) => pathname.startsWith(p));

  useEffect(() => {
    // Still loading auth state
    if (authEnabled === null) return;

    // Auth disabled - allow everything
    if (!authEnabled) return;

    // Auth enabled, not authenticated, not on a public path -> redirect to login
    if (!isAuthenticated && !isPublicPath) {
      router.replace("/login");
    }
  }, [isAuthenticated, authEnabled, isPublicPath, router]);

  // Still checking auth status - show loading
  if (authEnabled === null) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  // Auth enabled but not authenticated and not on public page
  if (authEnabled && !isAuthenticated && !isPublicPath) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  return <>{children}</>;
}
