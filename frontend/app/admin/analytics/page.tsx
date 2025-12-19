"use client";

import { useEffect, useState, useRef } from "react";
import { Upload, BarChart3, X, Loader2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Eye } from "lucide-react";

interface AnalyticsSnapshot {
  id: string;
  dataset_name: string;
  row_count: number | null;
  file_path: string | null;
  created_at: string;
  summary: Record<string, any>;
}

export default function AnalyticsPage() {
  const [snapshots, setSnapshots] = useState<AnalyticsSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSnapshot, setSelectedSnapshot] =
    useState<AnalyticsSnapshot | null>(null);

  // Upload state
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchSnapshots = async () => {
    try {
      const res = await fetch("/api/admin/analytics");
      if (!res.ok) throw new Error("Failed to fetch analytics");
      const data = await res.json();
      // Backend returns { data: [...], count: N }
      setSnapshots(Array.isArray(data) ? data : data.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSnapshots();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const lower = file.name.toLowerCase();
      if (!lower.endsWith(".csv") && !lower.endsWith(".xlsx")) {
        setUploadError("Only CSV or XLSX files are supported");
        return;
      }
      setSelectedFile(file);
      setDatasetName(file.name.replace(/\.(csv|xlsx)$/i, ""));
      setUploadError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append("file", selectedFile);
    if (datasetName) {
      formData.append("dataset_name", datasetName);
    }

    try {
      const res = await fetch("/api/ingest/data", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Upload failed");
      }

      const data = await res.json();
      setUploadSuccess(
        `Successfully uploaded "${data.dataset_name}" with ${data.row_count?.toLocaleString() || 0} rows`
      );
      setSelectedFile(null);
      setDatasetName("");
      if (fileInputRef.current) fileInputRef.current.value = "";

      // Refresh snapshots list
      fetchSnapshots();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const cancelUpload = () => {
    setSelectedFile(null);
    setDatasetName("");
    setUploadError(null);
    setUploadSuccess(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-secondary">Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-neon-red/10 border border-neon-red/30 rounded-lg p-4">
        <p className="text-neon-red">Error: {error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-text-primary font-display">
          Analytics Snapshots
        </h1>
        <Button
          onClick={() => setShowUpload(!showUpload)}
          className="bg-neon-cyan text-bg-primary hover:bg-cyan-500"
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload Dataset
        </Button>
      </div>

      {/* Upload Panel */}
      {showUpload && (
        <Card className="mb-6 border-neon-cyan/30 bg-neon-cyan/5 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 text-text-primary">
              <BarChart3 className="h-5 w-5 text-neon-cyan" />
              Upload Dataset (CSV or XLSX)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {uploadError && (
              <div className="bg-neon-red/10 border border-neon-red/30 rounded-lg p-3 text-neon-red text-sm">
                {uploadError}
              </div>
            )}
            {uploadSuccess && (
              <div className="bg-neon-green/10 border border-neon-green/30 rounded-lg p-3 text-neon-green text-sm">
                {uploadSuccess}
              </div>
            )}

            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                CSV or XLSX File
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileSelect}
                className="block w-full text-sm text-text-secondary
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-medium
                  file:bg-neon-cyan/20 file:text-neon-cyan
                  hover:file:bg-neon-cyan/30
                  cursor-pointer"
              />
            </div>

            {selectedFile && (
              <>
                {/* Dataset Name */}
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">
                    Dataset Name
                  </label>
                  <Input
                    value={datasetName}
                    onChange={(e) => setDatasetName(e.target.value)}
                    placeholder="Enter dataset name"
                    className="bg-bg-surface-2 border-border-default text-text-primary"
                  />
                  <p className="text-xs text-text-tertiary mt-1">
                    A descriptive name for this dataset (e.g., "outages_q4_2024", "load_forecast")
                  </p>
                </div>

                {/* File Info */}
                <div className="bg-bg-surface-2/50 rounded-lg p-3 border border-border-default">
                  <p className="text-sm text-text-secondary">
                    <span className="font-medium">Selected file:</span>{" "}
                    <span className="text-text-primary">{selectedFile.name}</span>
                  </p>
                  <p className="text-sm text-text-tertiary">
                    Size: {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="bg-neon-cyan text-bg-primary hover:bg-cyan-500"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Upload & Analyze
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={cancelUpload}
                    disabled={uploading}
                    className="border-border-default text-text-secondary hover:bg-bg-surface-2"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Snapshots Table */}
        <Card className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">All Snapshots</CardTitle>
          </CardHeader>
          <CardContent>
            {snapshots.length === 0 ? (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-text-tertiary mx-auto mb-3" />
                <p className="text-text-secondary">No analytics snapshots yet.</p>
                <p className="text-text-tertiary text-sm mt-1">
                  Click "Upload CSV" to add your first dataset.
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Dataset</TableHead>
                    <TableHead>Rows</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {snapshots.map((snap) => (
                    <TableRow
                      key={snap.id}
                      className={
                        selectedSnapshot?.id === snap.id ? "bg-neon-cyan/10" : ""
                      }
                    >
                      <TableCell>
                        <p className="font-medium text-sm text-text-primary">{snap.dataset_name}</p>
                      </TableCell>
                      <TableCell className="text-text-primary">
                        {snap.row_count?.toLocaleString() || "-"}
                      </TableCell>
                      <TableCell className="text-sm text-text-tertiary">
                        {new Date(snap.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedSnapshot(snap)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Summary Panel */}
        <Card className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg text-text-primary">
              {selectedSnapshot ? "Snapshot Details" : "Select a Snapshot"}
            </CardTitle>
            {selectedSnapshot && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedSnapshot(null)}
                className="text-text-tertiary hover:text-text-primary"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {!selectedSnapshot ? (
              <p className="text-text-secondary text-center py-8">
                Click on a snapshot to view details
              </p>
            ) : (
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-text-secondary">
                    Dataset Name
                  </p>
                  <p className="text-lg font-semibold text-text-primary">
                    {selectedSnapshot.dataset_name}
                  </p>
                </div>

                {selectedSnapshot.file_path && (
                  <div>
                    <p className="text-sm font-medium text-text-secondary">
                      File Path
                    </p>
                    <p className="text-sm text-text-tertiary break-all">
                      {selectedSnapshot.file_path}
                    </p>
                  </div>
                )}

                <SnapshotSummary summary={selectedSnapshot.summary} />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function SnapshotSummary({ summary }: { summary: Record<string, any> }) {
  const previewRows: Array<Record<string, any>> = summary?.preview_rows || [];
  const columnTypes = summary?.column_types || {};
  const categoryCounts = summary?.category_counts || {};
  const numericSummary = summary?.numeric_summary || {};
  const columns = summary?.columns || Object.keys(columnTypes);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <StatPill label="Rows" value={summary?.row_count ?? "-"} />
        <StatPill label="Columns" value={summary?.column_count ?? "-"} />
      </div>

      {columns?.length > 0 && (
        <div>
          <p className="text-sm font-medium text-text-secondary mb-1">Columns</p>
          <div className="flex flex-wrap gap-2">
            {columns.map((col: string) => (
              <span
                key={col}
                className="text-xs bg-bg-surface-3/50 border border-border-default px-2 py-1 rounded text-text-primary"
                title={columnTypes[col] || ""}
              >
                {col}
                {columnTypes[col] ? ` · ${columnTypes[col]}` : ""}
              </span>
            ))}
          </div>
        </div>
      )}

      {previewRows.length > 0 && (
        <div>
          <p className="text-sm font-medium text-text-secondary mb-1">Preview (first 5 rows)</p>
          <div className="border border-border-default rounded-lg overflow-hidden bg-bg-surface-3/40">
            <ScrollArea className="max-h-64">
              <table className="w-full text-xs text-text-primary">
                <thead className="bg-bg-surface-2/80">
                  <tr>
                    {columns.map((col: string) => (
                      <th
                        key={col}
                        className="text-left px-3 py-2 border-b border-border-default text-text-secondary"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewRows.map((row, idx) => (
                    <tr key={idx} className="border-b border-border-default/60 last:border-0">
                      {columns.map((col: string) => (
                        <td key={col} className="px-3 py-2 whitespace-pre-wrap align-top">
                          {String(row[col] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </ScrollArea>
          </div>
        </div>
      )}

      {Object.keys(numericSummary).length > 0 && (
        <div>
          <p className="text-sm font-medium text-text-secondary mb-1">Numeric Summary</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(numericSummary).map(([col, stats]) => (
              <div key={col} className="border border-border-default rounded-lg p-3 bg-bg-surface-3/40">
                <p className="text-xs font-semibold text-text-primary mb-1">{col}</p>
                <p className="text-xs text-text-secondary">min: {(stats as any).min ?? "-"}</p>
                <p className="text-xs text-text-secondary">mean: {(stats as any).mean ?? "-"}</p>
                <p className="text-xs text-text-secondary">max: {(stats as any).max ?? "-"}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(categoryCounts).length > 0 && (
        <div>
          <p className="text-sm font-medium text-text-secondary mb-1">Top Categories</p>
          <div className="space-y-2">
            {Object.entries(categoryCounts).map(([col, counts]) => (
              <div key={col} className="border border-border-default rounded-lg p-3 bg-bg-surface-3/40">
                <p className="text-xs font-semibold text-text-primary mb-2">{col}</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(counts as Record<string, number>).map(([val, count]) => (
                    <span
                      key={val}
                      className="text-[11px] bg-bg-surface-1 border border-border-default px-2 py-1 rounded text-text-secondary"
                    >
                      {val}: {count}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatPill({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border border-border-default rounded-lg px-3 py-2 bg-bg-surface-3/40">
      <p className="text-xs text-text-secondary">{label}</p>
      <p className="text-sm font-semibold text-text-primary">{value}</p>
    </div>
  );
}
