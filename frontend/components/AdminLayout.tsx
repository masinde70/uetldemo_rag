"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  MessageSquare, 
  FileText, 
  BarChart3, 
  Home, 
  Users,
  LogOut 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

/**
 * Navigation items for admin sidebar
 */
const navItems = [
  {
    href: "/admin",
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

interface AdminLayoutProps {
  children: React.ReactNode;
}

/**
 * AdminLayout Component
 * 
 * Provides the admin dashboard layout with:
 * - Fixed sidebar navigation
 * - Light topbar
 * - Scrollable main content area
 * 
 * Design: ERA Blue (#0033A0) primary, minimal white background
 */
export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-white">
      {/* Topbar */}
      <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6 fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            {/* ERA Blue logo */}
            <div 
              className="w-8 h-8 rounded flex items-center justify-center"
              style={{ backgroundColor: "#0033A0" }}
            >
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <span className="text-lg font-semibold text-slate-800">SISUiQ</span>
          </Link>
          <span className="text-slate-300">|</span>
          <span className="text-sm font-medium text-slate-600">
            Admin Dashboard
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="text-sm hover:underline"
            style={{ color: "#0033A0" }}
          >
            Back to Chat
          </Link>
          <Button
            variant="ghost"
            size="sm"
            className="text-slate-500 hover:text-slate-700"
          >
            <LogOut className="h-4 w-4 mr-1" />
            Logout
          </Button>
        </div>
      </header>

      <div className="flex pt-14">
        {/* Sidebar - Fixed */}
        <aside className="w-56 border-r border-slate-200 bg-white fixed left-0 top-14 bottom-0">
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
                      "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                      isActive
                        ? "font-medium"
                        : "text-slate-600 hover:bg-slate-50"
                    )}
                    style={isActive ? { 
                      backgroundColor: "rgba(0, 51, 160, 0.08)",
                      color: "#0033A0"
                    } : undefined}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            {/* Environment indicator */}
            <div className="absolute bottom-4 left-4 right-4">
              <div className="px-3 py-2 rounded-lg bg-slate-50 text-xs text-slate-500">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
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
