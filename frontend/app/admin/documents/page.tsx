"use client";

import { useEffect, useState, useRef } from "react";
import { Upload, FileText, X, Loader2, Trash2 } from "lucide-react";
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

interface Document {
  id: string;
  name: string;
  type: string;
  source: string;
  file_path: string;
  chunk_count: number;
  created_at: string;
}

const DOC_TYPES = ["strategy", "regulatory", "technical", "report", "policy", "other"];
const DOC_SOURCES = ["uetcl", "era", "memd", "world_bank", "other"];

type UploadItem = {
  id: string;
  file: File;
  name: string;
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Upload state
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<UploadItem[]>([]);
  const [docType, setDocType] = useState("strategy");
  const [docSource, setDocSource] = useState("uetcl");
  const [uploadingFileName, setUploadingFileName] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    try {
      const res = await fetch("/api/admin/documents");
      if (!res.ok) throw new Error("Failed to fetch documents");
      const data = await res.json();
      // Backend returns { data: [...], count: N }
      setDocuments(Array.isArray(data) ? data : data.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const pdfs = files.filter((file) => file.name.toLowerCase().endsWith(".pdf"));

    if (files.length > 0 && pdfs.length === 0) {
      setUploadError("Only PDF files are supported");
      return;
    }

    if (pdfs.length > 0) {
      const additions = pdfs.map((file) => ({
        id: `${file.name}-${crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2)}`,
        file,
        name: file.name.replace(/\.pdf$/i, ""),
      }));

      setSelectedFiles((prev) => [...prev, ...additions]);
      setUploadError(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    let successCount = 0;
    let failureCount = 0;
    let lastError = "";
    const completedIds = new Set<string>();

    for (const item of selectedFiles) {
      setUploadingFileName(item.file.name);

      const formData = new FormData();
      formData.append("file", item.file);
      formData.append("name", item.name || item.file.name);
      formData.append("doc_type", docType);
      formData.append("source", docSource);

      try {
        const res = await fetch("/api/ingest/docs", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || data.error || `Upload failed for ${item.file.name}`);
        }

        successCount += 1;
        completedIds.add(item.id);
      } catch (err) {
        failureCount += 1;
        lastError = err instanceof Error ? err.message : "Upload failed";
      }
    }

    setSelectedFiles((prev) => prev.filter((item) => !completedIds.has(item.id)));

    if (successCount > 0) {
      setUploadSuccess(
        `Uploaded ${successCount} file${successCount === 1 ? "" : "s"} successfully`
      );
      fetchDocuments();
    }

    if (failureCount > 0) {
      setUploadError(
        `Failed to upload ${failureCount} file${failureCount === 1 ? "" : "s"}. ${lastError}`
      );
    }

    setUploadingFileName(null);
    setUploading(false);
  };

  const cancelUpload = () => {
    setSelectedFiles([]);
    setUploadError(null);
    setUploadSuccess(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const updateQueuedName = (id: string, name: string) => {
    setSelectedFiles((prev) =>
      prev.map((item) => (item.id === id ? { ...item, name } : item))
    );
  };

  const removeQueuedFile = (id: string) => {
    setSelectedFiles((prev) => prev.filter((item) => item.id !== id));
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this document and its chunks?")) return;
    setDeletingId(id);
    setError(null);

    try {
      const res = await fetch(`/api/admin/documents/${id}`, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || data.error || "Failed to delete document");
      }

      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete document");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-secondary">Loading documents...</p>
      </div>
    );
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "strategy":
        return "bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30";
      case "regulation":
        return "bg-neon-violet/20 text-neon-violet border border-neon-violet/30";
      default:
        return "bg-bg-surface-3/50 text-text-secondary border border-border-default";
    }
  };

  const getSourceColor = (source: string) => {
    switch (source.toLowerCase()) {
      case "uetcl":
        return "bg-neon-green/20 text-neon-green border border-neon-green/30";
      case "era":
        return "bg-neon-orange/20 text-neon-orange border border-neon-orange/30";
      default:
        return "bg-bg-surface-3/50 text-text-secondary border border-border-default";
    }
  };

  return (
    <div>
      {error && (
        <div className="bg-neon-red/10 border border-neon-red/30 rounded-lg p-4 mb-4">
          <p className="text-neon-red">Error: {error}</p>
        </div>
      )}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-text-primary font-display">
          Ingested Documents
        </h1>
        <Button onClick={() => setShowUpload(!showUpload)} className="bg-neon-cyan text-bg-primary hover:bg-cyan-500">
          <Upload className="h-4 w-4 mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Upload Panel */}
      {showUpload && (
        <Card className="mb-6 border-neon-cyan/30 bg-neon-cyan/5 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 text-text-primary">
              <FileText className="h-5 w-5 text-neon-cyan" />
              Upload PDF Document
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
                PDF Files
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                multiple
                onChange={handleFileSelect}
                className="block w-full text-sm text-text-secondary
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-medium
                  file:bg-neon-cyan/20 file:text-neon-cyan
                  hover:file:bg-neon-cyan/30
                  cursor-pointer"
              />
              <p className="text-xs text-text-tertiary mt-1">
                You can select multiple PDFs; they will be processed sequentially.
              </p>
            </div>

            {selectedFiles.length > 0 && (
              <>
                {/* Upload queue */}
                <div className="space-y-3">
                  <div className="text-sm font-medium text-text-secondary flex items-center justify-between">
                    <span>Upload Queue ({selectedFiles.length})</span>
                    {uploadingFileName && (
                      <span className="text-xs text-text-tertiary">
                        Uploading: {uploadingFileName}
                      </span>
                    )}
                  </div>
                  {selectedFiles.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 border border-border-default rounded-lg px-3 py-2 bg-bg-surface-2/60"
                    >
                      <div className="flex-1 space-y-1">
                        <Input
                          value={item.name}
                          onChange={(e) => updateQueuedName(item.id, e.target.value)}
                          className="bg-bg-surface-1 border-border-default text-text-primary"
                          placeholder="Document name"
                          disabled={uploading}
                        />
                        <p className="text-xs text-text-tertiary truncate">
                          {item.file.name} · {(item.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeQueuedFile(item.id)}
                        disabled={uploading}
                        className="text-text-tertiary hover:text-neon-red"
                        title="Remove from queue"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>

                {/* Type and Source */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Document Type
                    </label>
                    <select
                      value={docType}
                      onChange={(e) => setDocType(e.target.value)}
                      className="w-full rounded-md border border-border-default bg-bg-surface-2 px-3 py-2 text-sm text-text-primary"
                    >
                      {DOC_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Source
                    </label>
                    <select
                      value={docSource}
                      onChange={(e) => setDocSource(e.target.value)}
                      className="w-full rounded-md border border-border-default bg-bg-surface-2 px-3 py-2 text-sm text-text-primary"
                    >
                      {DOC_SOURCES.map((source) => (
                        <option key={source} value={source}>
                          {source.toUpperCase()}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={handleUpload}
                    disabled={uploading || selectedFiles.length === 0}
                    className="bg-neon-cyan text-bg-primary hover:bg-cyan-500"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Upload {selectedFiles.length > 1 ? "All" : ""}{" "}
                        {selectedFiles.length} file{selectedFiles.length === 1 ? "" : "s"}
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={cancelUpload} disabled={uploading} className="border-border-default text-text-secondary hover:bg-bg-surface-2">
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      <Card className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg text-text-primary">All Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-text-tertiary mx-auto mb-3" />
              <p className="text-text-secondary">No documents ingested yet.</p>
              <p className="text-text-tertiary text-sm mt-1">
                Click "Upload Document" to add your first PDF.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Chunks</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium text-sm text-text-primary">{doc.name}</p>
                        <p className="text-xs text-text-tertiary truncate max-w-xs">
                          {doc.file_path}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 text-xs rounded ${getTypeColor(
                          doc.type
                        )}`}
                      >
                        {doc.type}
                      </span>
                    </TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 text-xs rounded ${getSourceColor(
                          doc.source
                        )}`}
                      >
                        {doc.source}
                      </span>
                    </TableCell>
                  <TableCell className="font-medium text-text-primary">{doc.chunk_count}</TableCell>
                  <TableCell className="text-sm text-text-tertiary">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-neon-red hover:text-neon-red"
                      onClick={() => handleDelete(doc.id)}
                      disabled={deletingId === doc.id}
                    >
                      {deletingId === doc.id ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </>
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        </CardContent>
      </Card>
    </div>
  );
}
