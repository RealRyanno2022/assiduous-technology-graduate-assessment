"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = window.localStorage.getItem("senus_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    const role = window.localStorage.getItem("senus_role");
    if (role) document.body.dataset.role = role;
    setReady(true);
  }, [router]);

  if (!ready) return null;
  return <>{children}</>;
}
