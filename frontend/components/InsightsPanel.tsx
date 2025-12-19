"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, BarChart3, Lightbulb, Zap, TrendingUp, AlertTriangle, Users, MapPin, FolderOpen } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { ChatMode } from "@/components/Sidebar";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

interface AnalyticsData {
  saidi?: number;
  saifi?: number;
  total_events?: number;
  total_customers_affected?: number;
  top_regions?: Array<{ region: string; events: number; percentage: number }>;
  outage_causes?: Record<string, number>;
  monthly_trend?: Array<{ month: string; events: number }>;
  note?: string;
  // Legacy format
  row_count?: number;
  date_range?: { min: string; max: string };
  category_counts?: Record<string, Record<string, number>>;
}

interface InsightsPanelProps {
  sources: string[];
  analytics?: AnalyticsData | null;
  mode?: ChatMode;
}

interface DocumentInfo {
  id: string;
  name: string;
  type: string;
  source: string;
  chunk_count: number;
}

// Mode-specific tips configuration based on available documents
const getModeTips = (docs: DocumentInfo[]): Record<ChatMode, { title: string; tips: string[]; examples: string[]; documents: string[]; hasRealDocs: boolean }> => {
  // Filter only documents with chunks (actually indexed)
  const indexedDocs = docs.filter(d => d.chunk_count > 0);
  
  // Group documents by source (case-insensitive)
  const uetclDocs = indexedDocs.filter(d => d.source.toLowerCase() === "uetcl").map(d => d.name);
  const eraDocs = indexedDocs.filter(d => d.source.toLowerCase() === "era").map(d => d.name);
  const allDocNames = indexedDocs.map(d => d.name);
  
  // Check for specific document types
  const hasStrategicDocs = indexedDocs.some(d => 
    d.name.toLowerCase().includes("strategic") || 
    d.name.toLowerCase().includes("grid") ||
    d.name.toLowerCase().includes("plan")
  );
  const hasPPADocs = indexedDocs.some(d => 
    d.name.toLowerCase().includes("ppa") || 
    d.name.toLowerCase().includes("getfit") ||
    d.name.toLowerCase().includes("get-fit")
  );
  const hasConnectionDocs = indexedDocs.some(d => 
    d.name.toLowerCase().includes("connection") || 
    d.name.toLowerCase().includes("customer")
  );
  const hasTariffDocs = indexedDocs.some(d => 
    d.name.toLowerCase().includes("tariff")
  );
  
  // Generate dynamic examples based on actual documents
  const generateExamples = (docNames: string[]): string[] => {
    if (docNames.length === 0) return ["Upload documents to enable Q&A"];
    const examples: string[] = [];
    if (hasPPADocs) {
      examples.push("Explain the key terms of the GET FIT PPA agreement");
    }
    if (hasConnectionDocs) {
      examples.push("What is the customer connection cost methodology?");
    }
    if (hasStrategicDocs) {
      examples.push("What are the key strategic objectives and timelines?");
    }
    if (hasTariffDocs) {
      examples.push("Explain the bulk supply tariff calculation method");
    }
    return examples.length > 0 ? examples : docNames.slice(0, 2).map(d => `Summarize the ${d} document`);
  };
  
  // Generate dynamic tips based on what's actually indexed
  const generateStrategyTips = (): string[] => {
    if (allDocNames.length === 0) {
      return [
        "No documents indexed yet",
        "Upload documents via /admin to enable Q&A",
        "The AI needs documents to answer questions"
      ];
    }
    const tips: string[] = ["Reference specific indexed documents by name"];
    if (hasStrategicDocs) {
      tips.push("Ask about KPIs, targets, and timelines");
    } else {
      tips.push("⚠️ No strategic plan docs - KPI questions may not work");
    }
    if (hasPPADocs) {
      tips.push("Ask about PPA terms and GET FIT agreements");
    }
    if (hasConnectionDocs) {
      tips.push("Ask about connection costs and customer policies");
    }
    tips.push("The AI can only answer from indexed documents");
    return tips.slice(0, 4); // Max 4 tips
  };
  
  return {
    strategy_qa: {
      title: "Strategy Q&A",
      documents: allDocNames,
      hasRealDocs: allDocNames.length > 0,
      tips: generateStrategyTips(),
      examples: generateExamples(allDocNames)
    },
    actions: {
      title: "Action Planner",
      documents: allDocNames,
      hasRealDocs: allDocNames.length > 0,
      tips: allDocNames.length > 0 ? [
        "Describe your specific challenge or goal",
        "Ask for prioritized, actionable steps",
        hasPPADocs ? "Reference PPA agreements for action items" : "Reference available documents for context"
      ] : [
        "No documents indexed yet",
        "Action planning requires indexed documents",
        "Upload planning documents first"
      ],
      examples: hasPPADocs ? [
        "What actions are required under the GET FIT agreement?",
        "Create an implementation checklist from the PPA",
        "What are the next steps for grid connection?"
      ] : generateExamples(allDocNames)
    },
    analytics: {
      title: "Analytics + Strategy",
      documents: allDocNames,
      hasRealDocs: allDocNames.length > 0,
      tips: [
        "Ask about SAIDI/SAIFI trends and patterns",
        "Compare performance against targets",
        "Request regional breakdown analysis"
      ],
      examples: [
        "Show me the outage trends analysis",
        "Which regions have the highest fault rates?",
        "How does performance compare to targets?"
      ]
    },
    regulatory: {
      title: "Regulatory Advisor",
      documents: eraDocs.length > 0 ? eraDocs : allDocNames,
      hasRealDocs: eraDocs.length > 0,
      tips: eraDocs.length > 0 ? [
        "Ask about specific ERA compliance requirements",
        "Reference license conditions and obligations",
        "Inquire about tariff structures"
      ] : [
        "⚠️ No ERA documents indexed",
        "Upload ERA guidelines to enable regulatory Q&A",
        "Currently using general documents only"
      ],
      examples: eraDocs.length > 0 ? [
        "What are ERA's reporting requirements?",
        "Explain the tariff calculation method",
        "What performance standards must UETCL meet?"
      ] : [
        "Summarize regulatory aspects from available docs",
        "What compliance requirements are mentioned?",
        "What regulatory frameworks apply?"
      ]
    }
  };
};

export function InsightsPanel({ sources, analytics, mode = "strategy_qa" }: InsightsPanelProps) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const REFRESH_INTERVAL_MS = 30_000; // periodic refresh

  const hasAnalytics = analytics && Object.keys(analytics).length > 0;
  const hasDemoData = analytics?.saidi !== undefined;

  // Fetch documents on mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch("/api/admin/documents", {
          headers: {
            "Authorization": "Bearer demo-admin-token-change-me"
          }
        });
        if (response.ok) {
          const data = await response.json();
          setDocuments(data.data || []);
        }
      } catch (error) {
        console.error("Failed to fetch documents:", error);
      } finally {
        setIsLoadingDocs(false);
      }
    };
    fetchDocuments();

    const interval = setInterval(() => {
      fetchDocuments();
    }, REFRESH_INTERVAL_MS);

    return () => clearInterval(interval);
  }, []);
  
  const modeTips = getModeTips(documents);
  const currentTips = modeTips[mode];

  return (
    <aside className="w-80 border-l border-border-default/50 bg-bg-surface-1/40 backdrop-blur-md flex flex-col" data-testid="insights-panel">
      <div className="p-4 border-b border-border-default/50 bg-transparent text-text-primary">
        <h2 className="text-sm font-semibold font-display">Insights</h2>
      </div>

      <ScrollArea className="flex-1 p-4 space-y-4">
        {/* Analytics KPIs Section */}
        {hasDemoData && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card className="border-neon-cyan/30 bg-bg-surface-2/70 backdrop-blur-sm shadow-glow-cyan/10">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2 text-text-primary font-display">
                  <BarChart3 className="h-4 w-4 text-neon-cyan" />
                  Key Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* SAIDI & SAIFI */}
                <div className="grid grid-cols-2 gap-3">
                  {analytics.saidi !== undefined && (
                    <div className="bg-gradient-to-br from-neon-cyan/20 to-neon-cyan/5 rounded-xl p-3 border border-neon-cyan/40 shadow-glow-cyan/20">
                      <div className="flex items-center gap-1.5 mb-2">
                        <Zap className="h-4 w-4 text-neon-cyan" />
                        <span className="text-xs text-neon-cyan font-bold uppercase tracking-wider">SAIDI</span>
                      </div>
                      <p className="text-2xl font-bold text-white drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]">{analytics.saidi}</p>
                      <p className="text-[10px] text-text-secondary mt-1">Duration Index</p>
                    </div>
                  )}
                  {analytics.saifi !== undefined && (
                    <div className="bg-gradient-to-br from-neon-violet/20 to-neon-violet/5 rounded-xl p-3 border border-neon-violet/40 shadow-glow-violet/20">
                      <div className="flex items-center gap-1.5 mb-2">
                        <TrendingUp className="h-4 w-4 text-neon-violet" />
                        <span className="text-xs text-neon-violet font-bold uppercase tracking-wider">SAIFI</span>
                      </div>
                      <p className="text-2xl font-bold text-white drop-shadow-[0_0_8px_rgba(168,85,247,0.5)]">{analytics.saifi}</p>
                      <p className="text-[10px] text-text-secondary mt-1">Frequency Index</p>
                    </div>
                  )}
                </div>

                {/* Regional Breakdown - Recharts Upgrade */}
                {analytics.top_regions && analytics.top_regions.length > 0 && (
                  <div className="bg-bg-surface-3/40 rounded-xl p-4 border border-border-emphasis/50">
                    <div className="flex items-center gap-2 mb-4">
                      <MapPin className="h-4 w-4 text-neon-cyan" />
                      <span className="text-xs text-text-primary font-bold uppercase tracking-wider">Regional Impact</span>
                    </div>
                    <div className="h-32 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={analytics.top_regions.slice(0, 4)} layout="vertical">
                          <XAxis type="number" hide />
                          <YAxis
                            dataKey="region"
                            type="category"
                            hide
                          />
                          <Tooltip
                            cursor={{ fill: 'rgba(34, 211, 238, 0.05)' }}
                            content={({ active, payload }: any) => {
                              if (active && payload && payload.length) {
                                return (
                                  <div className="bg-bg-surface-3 border border-border-default p-2 rounded shadow-lg">
                                    <p className="text-[10px] text-text-primary font-bold">{payload[0].payload.region}</p>
                                    <p className="text-[10px] text-neon-cyan">{payload[0].value}% Impact</p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Bar
                            dataKey="percentage"
                            radius={[0, 4, 4, 0]}
                            barSize={12}
                          >
                            {analytics.top_regions.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={index === 0 ? '#22D3EE' : '#22D3EE80'}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-3 space-y-2">
                      {analytics.top_regions.slice(0, 3).map((r, i) => (
                        <div key={i} className="flex justify-between text-xs text-text-primary">
                          <span className="font-medium">{r.region}</span>
                          <span className="text-neon-cyan font-bold">{r.percentage}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Sources Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="border-border-default bg-bg-surface-2/30 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2 text-text-primary font-display">
                <FileText className="h-4 w-4 text-neon-cyan" />
                Sources
              </CardTitle>
            </CardHeader>
            <CardContent>
              {sources.length > 0 ? (
                <ul className="space-y-2">
                  {sources.map((source, idx) => (
                    <li
                      key={idx}
                      className="text-xs text-text-secondary bg-bg-surface-3/30 rounded px-2 py-1.5 border border-border-default/30 break-words overflow-hidden"
                      title={source}
                    >
                      <span className="line-clamp-2">{source}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-text-tertiary italic">
                  No sources cited yet
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Legacy Analytics Section */}
        {hasAnalytics && !hasDemoData && (
          <Card className="border-border-default bg-bg-surface-2/30 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2 text-text-primary font-display">
                <BarChart3 className="h-4 w-4 text-neon-cyan" />
                Analytics Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {analytics.row_count && (
                <div className="flex justify-between text-xs">
                  <span className="text-text-tertiary">Records</span>
                  <span className="font-medium text-text-primary">
                    {analytics.row_count.toLocaleString()}
                  </span>
                </div>
              )}
              {analytics.date_range && (
                <div className="text-xs">
                  <span className="text-text-tertiary block mb-1">Date Range</span>
                  <span className="font-medium text-text-primary">
                    {new Date(analytics.date_range.min).toLocaleDateString()} -{" "}
                    {new Date(analytics.date_range.max).toLocaleDateString()}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Mode-Specific Tips Section */}
        <motion.div
          key={mode}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="border-neon-yellow/30 bg-bg-surface-2/30 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2 text-text-primary font-display">
                <Lightbulb className="h-4 w-4 text-neon-yellow" />
                {currentTips.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Available Documents for this mode */}
              <div>
                <p className="text-[10px] uppercase tracking-wider text-text-tertiary mb-2 font-semibold flex items-center gap-1">
                  <FolderOpen className="h-3 w-3" />
                  Indexed Documents
                  {!currentTips.hasRealDocs && mode === "regulatory" && (
                    <span className="ml-1 text-neon-yellow">⚠️</span>
                  )}
                </p>
                {currentTips.documents.length > 0 ? (
                  <ul className="space-y-1.5">
                    {currentTips.documents.slice(0, 4).map((doc, idx) => (
                      <li 
                        key={idx} 
                        className="text-xs text-text-secondary flex items-center gap-2"
                      >
                        <FileText className="h-3 w-3 text-neon-cyan flex-shrink-0" />
                        <span className="truncate">{doc}</span>
                      </li>
                    ))}
                    {currentTips.documents.length > 4 && (
                      <li className="text-xs text-text-tertiary italic pl-5">
                        +{currentTips.documents.length - 4} more documents
                      </li>
                    )}
                  </ul>
                ) : (
                  <div className="text-xs text-neon-yellow bg-neon-yellow/10 rounded-lg px-3 py-2 border border-neon-yellow/30">
                    <p className="font-medium">No documents indexed</p>
                    <p className="text-text-tertiary mt-1">Upload documents via Admin → Documents</p>
                  </div>
                )}
                {!currentTips.hasRealDocs && mode === "regulatory" && currentTips.documents.length > 0 && (
                  <p className="text-[10px] text-neon-yellow mt-2 italic">
                    ⚠️ No ERA-specific documents. Using general docs.
                  </p>
                )}
              </div>
              
              {/* Tips */}
              <div>
                <p className="text-[10px] uppercase tracking-wider text-text-tertiary mb-2 font-semibold">Tips</p>
                <ul className="space-y-2 text-xs text-text-secondary">
                  {currentTips.tips.map((tip, idx) => (
                    <li key={idx} className="flex gap-2">
                      <span className={tip.startsWith("⚠️") ? "text-neon-yellow" : "text-neon-yellow font-bold"}>{tip.startsWith("⚠️") ? "" : "•"}</span>
                      <span className={tip.startsWith("⚠️") ? "text-neon-yellow" : ""}>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Example Questions */}
              <div>
                <p className="text-[10px] uppercase tracking-wider text-text-tertiary mb-2 font-semibold">Try Asking</p>
                <ul className="space-y-2">
                  {currentTips.examples.map((example, idx) => (
                    <li 
                      key={idx} 
                      className="text-xs text-text-secondary bg-bg-surface-3/50 rounded-lg px-3 py-2 border border-border-default/30 hover:border-neon-cyan/30 hover:bg-bg-surface-3/70 transition-colors cursor-pointer"
                    >
                      <span className="text-neon-cyan mr-1">"</span>
                      {example}
                      <span className="text-neon-cyan ml-1">"</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </motion.div>

      </ScrollArea>
    </aside>
  );
}
