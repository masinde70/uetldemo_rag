"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { MessageSquare, FileText, BarChart3, Home, Users, LogOut, Shield, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MeshBackground } from "@/components/ui/MeshBackground";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { AuthProvider, useAuth } from "@/lib/auth";

const navItems = [
  {
    href: "/admin/dashboard",
    label: "Overview",
    icon: Home,
    exact: true,
  },
  {
    href: "/admin/users",
    label: "Users",
    icon: Users,
  },
  {
    href: "/admin/sessions",
    label: "Sessions",
    icon: MessageSquare,
  },
  {
    href: "/admin/documents",
    label: "Documents",
    icon: FileText,
  },
  {
    href: "/admin/analytics",
    label: "Analytics",
    icon: BarChart3,
  },
];

function AdminLayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading, logout, user } = useAuth();

  // Redirect to login if not authenticated or not admin (except on login page)
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isAdmin) && pathname !== "/admin/login") {
      router.push("/admin/login");
    }
  }, [isLoading, isAuthenticated, isAdmin, pathname, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <MeshBackground />
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
            <Shield className="h-8 w-8 text-primary" />
          </div>
          <Loader2 className="h-6 w-6 text-primary animate-spin" />
          <p className="text-text-secondary">Verifying access...</p>
        </div>
      </div>
    );
  }

  // Login page gets its own layout (no sidebar)
  if (pathname === "/admin/login") {
    return <>{children}</>;
  }

  // Not authenticated or not admin - redirect handled by useEffect
  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  const handleLogout = async () => {
    await logout();
    router.push("/admin/login");
  };

  return (
    <div className="min-h-screen bg-background">
      <MeshBackground />

      {/* Topbar */}
      <header className="h-14 border-b border-border-default/50 bg-bg-surface-1/80 backdrop-blur-md flex items-center justify-between px-6 fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center dark:shadow-glow-cyan/20">
              <span className="text-primary-foreground font-bold text-sm">S</span>
            </div>
            <span className="text-lg font-semibold text-text-primary font-display">SISUiQ</span>
          </Link>
          <span className="text-border-default">|</span>
          <span className="text-sm font-medium text-text-secondary">
            Admin Dashboard
          </span>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link
            href="/"
            className="text-sm text-primary hover:text-primary/80 transition-colors"
          >
            Back to Chat
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-text-tertiary hover:text-text-primary hover:bg-bg-surface-2"
          >
            <LogOut className="h-4 w-4 mr-1" />
            Logout
          </Button>
        </div>
      </header>

      <div className="flex pt-14">
        {/* Sidebar - Fixed */}
        <aside className="w-56 border-r border-border-default/50 bg-bg-surface-1/60 backdrop-blur-md fixed left-0 top-14 bottom-0">
          <ScrollArea className="h-full">
            <nav className="p-4 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = item.exact
                  ? pathname === item.href
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 relative",
                      isActive
                        ? "bg-primary/15 text-primary font-medium border border-primary/30 dark:shadow-glow-cyan before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:bg-primary before:rounded-full"
                        : "text-text-secondary hover:bg-bg-surface-2 hover:text-text-primary"
                    )}
                  >
                    <Icon className={cn("h-4 w-4", isActive ? "text-primary" : "")} />
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            {/* Environment indicator */}
            <div className="absolute bottom-4 left-4 right-4">
              <div className="px-3 py-2 rounded-lg bg-bg-surface-2/50 border border-border-default/50 text-xs text-text-tertiary">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-success dark:shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                  Development
                </div>
              </div>
            </div>
          </ScrollArea>
        </aside>

        {/* Main content - Scrollable */}
        <main className="flex-1 ml-56 p-6 min-h-[calc(100vh-3.5rem)]">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <AdminLayoutContent>{children}</AdminLayoutContent>
    </AuthProvider>
  );
}
