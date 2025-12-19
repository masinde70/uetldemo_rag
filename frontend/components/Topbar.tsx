"use client";

import Link from "next/link";
import { User, Settings, LogOut, Shield, ChevronDown } from "lucide-react";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

interface TopbarProps {
  userEmail?: string;
  userRole?: "admin" | "user";
  onSignOut?: () => Promise<void> | void;
}

export function Topbar({ 
  userEmail = "demo@uetcl.go.ug",
  userRole = "admin",  // Default to admin for demo
  onSignOut
}: TopbarProps) {
  const initials = userEmail
    .split("@")[0]
    .slice(0, 2)
    .toUpperCase();

  const isAdmin = userRole === "admin";

  const handleSignOut = async () => {
    // Call the backend logout endpoint to clear HttpOnly cookies
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Ignore errors - we're logging out anyway
    }
    
    // Call custom handler if provided
    if (onSignOut) {
      await onSignOut();
    } else {
      // Default: redirect to home
      window.location.href = "/";
    }
  };

  return (
    <header className="h-14 border-b border-border-default/50 bg-bg-surface-1/40 backdrop-blur-md flex items-center justify-between px-6 z-50 relative">
      <div className="flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 rounded bg-primary flex items-center justify-center dark:shadow-glow-cyan/20">
            <span className="text-primary-foreground font-bold text-sm">S</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-text-primary font-display">SISUiQ</h1>
          </div>
        </Link>
        <span className="text-border-default">|</span>
        <span className="text-sm text-text-secondary">
          ERA/UETCL Strategy Copilot
        </span>
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />
        
        {/* Admin Quick Access - visible only to admins */}
        {isAdmin && (
          <Link href="/admin/login">
            <Button 
              variant="ghost" 
              size="sm"
              className="text-text-tertiary hover:text-primary hover:bg-primary/10"
            >
              <Shield className="h-4 w-4 mr-1.5" />
              <span className="hidden sm:inline">Admin</span>
            </Button>
          </Link>
        )}

        {/* User Menu Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="ghost" 
              className="flex items-center gap-2 px-2 hover:bg-bg-surface-2"
            >
              <div className="w-8 h-8 rounded-full bg-bg-surface-2 flex items-center justify-center border border-border-default">
                {initials ? (
                  <span className="text-text-primary font-medium text-xs">{initials}</span>
                ) : (
                  <User className="h-4 w-4 text-text-secondary" />
                )}
              </div>
              <div className="hidden md:flex flex-col items-start">
                <span className="text-sm text-text-primary font-medium">
                  {userEmail.split("@")[0]}
                </span>
                <span className="text-xs text-text-tertiary capitalize">
                  {userRole}
                </span>
              </div>
              <ChevronDown className="h-4 w-4 text-text-tertiary" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium">{userEmail}</p>
                <p className="text-xs text-text-tertiary capitalize">
                  {userRole} account
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            
            {isAdmin && (
              <>
                <DropdownMenuItem asChild>
                  <Link href="/admin/login" className="cursor-pointer">
                    <Shield className="mr-2 h-4 w-4" />
                    Admin Dashboard
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/admin/login" className="cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    Manage Documents
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
              </>
            )}
            
            <DropdownMenuItem 
              onClick={handleSignOut}
              className="text-neon-red focus:text-neon-red cursor-pointer"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
