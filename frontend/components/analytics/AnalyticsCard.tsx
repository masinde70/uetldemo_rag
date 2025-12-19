"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, AlertTriangle, Users, Zap, MapPin } from "lucide-react";

interface AnalyticsData {
  saidi?: number;
  saifi?: number;
  total_events?: number;
  total_customers_affected?: number;
  top_regions?: Array<{ region: string; events: number; percentage: number }>;
  outage_causes?: Record<string, number>;
  monthly_trend?: Array<{ month: string; events: number }>;
  note?: string;
}

interface AnalyticsCardProps {
  data: AnalyticsData;
}

export function AnalyticsCard({ data }: AnalyticsCardProps) {
  return (
    <div className="space-y-4 my-4">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {data.saidi !== undefined && (
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-blue-600 font-medium">SAIDI</p>
                  <p className="text-2xl font-bold text-blue-800">{data.saidi}</p>
                  <p className="text-xs text-blue-500">Avg. Duration</p>
                </div>
                <Zap className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>
        )}

        {data.saifi !== undefined && (
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-purple-600 font-medium">SAIFI</p>
                  <p className="text-2xl font-bold text-purple-800">{data.saifi}</p>
                  <p className="text-xs text-purple-500">Avg. Frequency</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>
        )}

        {data.total_events !== undefined && (
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-orange-600 font-medium">Events</p>
                  <p className="text-2xl font-bold text-orange-800">
                    {data.total_events.toLocaleString()}
                  </p>
                  <p className="text-xs text-orange-500">Total Outages</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>
        )}

        {data.total_customers_affected !== undefined && (
          <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-red-600 font-medium">Customers</p>
                  <p className="text-2xl font-bold text-red-800">
                    {data.total_customers_affected.toLocaleString()}
                  </p>
                  <p className="text-xs text-red-500">Affected</p>
                </div>
                <Users className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Regional and Causes Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Regional Breakdown */}
        {data.top_regions && data.top_regions.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <MapPin className="h-4 w-4 text-slate-500" />
                Regional Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.top_regions.map((region) => (
                  <div key={region.region}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">{region.region}</span>
                      <span className="text-slate-500">
                        {region.events} ({region.percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${region.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Outage Causes */}
        {data.outage_causes && Object.keys(data.outage_causes).length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-slate-500" />
                Outage Causes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(data.outage_causes)
                  .sort(([, a], [, b]) => b - a)
                  .map(([cause, percentage]) => (
                    <div key={cause}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium capitalize">
                          {cause.replace(/_/g, " ")}
                        </span>
                        <span className="text-slate-500">{percentage}%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            cause === "equipment_failure"
                              ? "bg-red-500"
                              : cause === "weather"
                              ? "bg-blue-500"
                              : cause === "vegetation"
                              ? "bg-green-500"
                              : cause === "third_party"
                              ? "bg-yellow-500"
                              : "bg-slate-500"
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Monthly Trend */}
      {data.monthly_trend && data.monthly_trend.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-slate-500" />
              Monthly Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between h-24 gap-2">
              {data.monthly_trend.map((month) => {
                const maxEvents = Math.max(...data.monthly_trend!.map((m) => m.events));
                const heightPercent = (month.events / maxEvents) * 100;
                return (
                  <div key={month.month} className="flex flex-col items-center flex-1">
                    <div
                      className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all duration-500"
                      style={{ height: `${heightPercent}%` }}
                    />
                    <p className="text-xs text-slate-500 mt-1 truncate w-full text-center">
                      {month.month.split(" ")[0]}
                    </p>
                    <p className="text-xs font-semibold">{month.events}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Note */}
      {data.note && (
        <p className="text-xs text-slate-500 italic text-center">{data.note}</p>
      )}
    </div>
  );
}
