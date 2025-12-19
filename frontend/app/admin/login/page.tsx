"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Shield, Eye, EyeOff, AlertCircle, ArrowLeft, Loader2, Mail, Lock } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MeshBackground } from "@/components/ui/MeshBackground";
import { useAuth } from "@/lib/auth";
import { motion } from "framer-motion";

export default function AdminLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const { login, isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();

  // Redirect to dashboard if already authenticated as admin
  useEffect(() => {
    if (!authLoading && isAuthenticated && isAdmin) {
      router.replace("/admin/dashboard");
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const result = await login(email, password);
    
    if (result.success) {
      router.push("/admin/dashboard");
    } else {
      setError(result.error || "Invalid credentials");
    }
    
    setIsSubmitting(false);
  };

  // Show loading while checking auth state
  if (authLoading) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
        <MeshBackground />
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
            <Shield className="h-8 w-8 text-primary" />
          </div>
          <Loader2 className="h-6 w-6 text-primary animate-spin" />
          <p className="text-text-secondary">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Don't render login form if authenticated (redirect in progress)
  if (isAuthenticated && isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
      <MeshBackground />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Back to Chat Link */}
        <Link 
          href="/"
          className="inline-flex items-center gap-2 text-text-tertiary hover:text-text-primary transition-colors mb-8"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Chat
        </Link>

        {/* Login Card */}
        <div className="bg-bg-surface-1/80 backdrop-blur-md border border-border-default rounded-xl p-8 shadow-xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-xl bg-primary/20 flex items-center justify-center mx-auto mb-4 border border-primary/30">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary font-display">
              Admin Login
            </h1>
            <p className="text-text-secondary mt-2">
              Sign in with your admin credentials
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div className="space-y-2">
              <label 
                htmlFor="email" 
                className="text-sm font-medium text-text-secondary"
              >
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@example.com"
                  className="pl-10 bg-bg-surface-2 border-border-default"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label 
                htmlFor="password" 
                className="text-sm font-medium text-text-secondary"
              >
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="pl-10 pr-10 bg-bg-surface-2 border-border-default"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-3 rounded-lg bg-neon-red/10 border border-neon-red/30 text-neon-red text-sm"
              >
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {error}
              </motion.div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting || !email.trim() || !password.trim()}
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          {/* Security Notice */}
          <div className="mt-6 pt-6 border-t border-border-default">
            <p className="text-xs text-text-tertiary text-center">
              Secure login with HttpOnly cookies and JWT tokens.
              <br />
              Your session will expire after 15 minutes of inactivity.
            </p>
          </div>
        </div>

        {/* Demo Credentials */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 p-4 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30"
        >
          <p className="text-sm text-neon-cyan text-center">
            <strong>Demo credentials:</strong>
            <br />
            Email: <code className="px-1 py-0.5 bg-bg-surface-2 rounded">admin@sisuiq.local</code>
            <br />
            Password: <code className="px-1 py-0.5 bg-bg-surface-2 rounded">admin123</code>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
