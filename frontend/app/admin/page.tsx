"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Shield } from "lucide-react";
import { MeshBackground } from "@/components/ui/MeshBackground";

export default function AdminIndexPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to login page - auth will then redirect to dashboard if authenticated
    router.replace("/admin/login");
  }, [router]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <MeshBackground />
      <div className="flex flex-col items-center gap-4">
        <div className="w-16 h-16 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
          <Shield className="h-8 w-8 text-primary" />
        </div>
        <Loader2 className="h-6 w-6 text-primary animate-spin" />
        <p className="text-text-secondary">Redirecting...</p>
      </div>
    </div>
  );
}
