"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  MessageSquare,
  FileText,
  BarChart3,
  Users,
  Layers,
  Cpu,
  Activity,
  MessageSquare as MessageSquareIcon,
  Sparkles,
  Database,
} from "lucide-react";

interface Stats {
  users: number;
  sessions: number;
  messages: number;
  documents: number;
  chunks: number;
  analytics_snapshots: number;
}

export default function AdminOverview() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/api/admin/stats");
        if (!res.ok) throw new Error("Failed to fetch stats");
        const data = await res.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-secondary">Loading statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-neon-red/10 border border-neon-red/30 rounded-lg p-4">
        <p className="text-neon-red">Error: {error}</p>
        <p className="text-sm text-neon-red/70 mt-1">
          Make sure the backend is running and ADMIN_TOKEN is configured.
        </p>
      </div>
    );
  }

  const statCards = [
    {
      label: "Users",
      value: stats?.users || 0,
      icon: Users,
      color: "text-neon-cyan",
      bgColor: "bg-neon-cyan/10",
      borderColor: "border-neon-cyan/30",
    },
    {
      label: "Sessions",
      value: stats?.sessions || 0,
      icon: MessageSquare,
      color: "text-neon-green",
      bgColor: "bg-neon-green/10",
      borderColor: "border-neon-green/30",
    },
    {
      label: "Messages",
      value: stats?.messages || 0,
      icon: MessageSquare,
      color: "text-neon-violet",
      bgColor: "bg-neon-violet/10",
      borderColor: "border-neon-violet/30",
    },
    {
      label: "Documents",
      value: stats?.documents || 0,
      icon: FileText,
      color: "text-neon-orange",
      bgColor: "bg-neon-orange/10",
      borderColor: "border-neon-orange/30",
    },
    {
      label: "Chunks",
      value: stats?.chunks || 0,
      icon: Layers,
      color: "text-neon-cyan",
      bgColor: "bg-neon-cyan/10",
      borderColor: "border-neon-cyan/30",
    },
    {
      label: "Analytics",
      value: stats?.analytics_snapshots || 0,
      icon: BarChart3,
      color: "text-neon-yellow",
      bgColor: "bg-neon-yellow/10",
      borderColor: "border-neon-yellow/30",
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text-primary font-display mb-6">
        Admin Overview
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-text-secondary">
                  {stat.label}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor} border ${stat.borderColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-text-primary">
                  {stat.value.toLocaleString()}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* System Info */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="border-border-default bg-bg-surface-2/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2 text-text-primary font-display">
              <Cpu className="h-4 w-4 text-neon-violet" />
              System Info
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-3.5 w-3.5 text-neon-cyan" />
                <span className="text-xs text-text-secondary">Documents</span>
              </div>
              <span className="text-xs font-medium text-text-primary bg-bg-surface-3/50 px-2 py-0.5 rounded">
                {(stats?.documents ?? 0).toLocaleString()} indexed
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-3.5 w-3.5 text-neon-yellow" />
                <span className="text-xs text-text-secondary">Chunks</span>
              </div>
              <span className="text-xs font-medium text-text-primary bg-bg-surface-3/50 px-2 py-0.5 rounded">
                {(stats?.chunks ?? 0).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-3.5 w-3.5 text-neon-cyan" />
                <span className="text-xs text-text-secondary">Model</span>
              </div>
              <span className="text-xs font-medium text-text-primary bg-bg-surface-3/50 px-2 py-0.5 rounded">
                GPT-4o
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquareIcon className="h-3.5 w-3.5 text-neon-yellow" />
                <span className="text-xs text-text-secondary">Embeddings</span>
              </div>
              <span className="text-xs font-medium text-text-primary bg-bg-surface-3/50 px-2 py-0.5 rounded">
                text-embedding-3-small
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="h-3.5 w-3.5 text-neon-green" />
                <span className="text-xs text-text-secondary">Status</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
                <span className="text-xs font-medium text-neon-green">Online</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-3.5 w-3.5 text-neon-violet" />
                <span className="text-xs text-text-secondary">Vector DB</span>
              </div>
              <span className="text-xs font-medium text-text-primary bg-bg-surface-3/50 px-2 py-0.5 rounded">
                Qdrant
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 p-4 bg-neon-yellow/10 border border-neon-yellow/30 rounded-lg">
        <p className="text-neon-yellow text-sm">
          <strong>Note:</strong> This is a demo admin dashboard. In production,
          implement proper authentication and authorization.
        </p>
      </div>
    </div>
  );
}
