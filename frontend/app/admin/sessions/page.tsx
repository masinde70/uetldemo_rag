"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, X, ExternalLink } from "lucide-react";
import {
  fetchSessions,
  fetchSessionMessages,
  formatDate,
  getModeDisplayName,
  type Session,
  type Message,
} from "@/lib/api";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await fetchSessions(50, 0);
        setSessions(response.data);
        setTotalCount(response.count || 0);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch sessions");
      } finally {
        setLoading(false);
      }
    };

    loadSessions();
  }, []);

  const viewMessages = async (sessionId: string) => {
    setSelectedSession(sessionId);
    setLoadingMessages(true);
    try {
      const response = await fetchSessionMessages(sessionId);
      setMessages(response.data);
    } catch (err) {
      console.error("Error fetching messages:", err);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const closeMessages = () => {
    setSelectedSession(null);
    setMessages([]);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-secondary">Loading sessions...</p>
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
        <h1 className="text-2xl font-semibold text-text-primary font-display">Chat Sessions</h1>
        <span className="text-sm text-text-tertiary">
          {totalCount} total session{totalCount !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sessions Table */}
        <Card className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">All Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <p className="text-text-secondary text-center py-8">
                No sessions found
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Mode</TableHead>
                    <TableHead>Messages</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.map((session) => (
                    <TableRow
                      key={session.id}
                      data-testid="admin-session-row"
                      className={
                        selectedSession === session.id ? "bg-neon-cyan/10" : ""
                      }
                    >
                      <TableCell>
                        <div>
                          <p className="font-medium text-sm text-text-primary">
                            {session.user_name}
                          </p>
                          <p className="text-xs text-text-tertiary">
                            {session.user_email}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span 
                          className="px-2 py-1 text-xs rounded font-medium bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30"
                        >
                          {getModeDisplayName(session.mode)}
                        </span>
                      </TableCell>
                      <TableCell className="text-text-primary">{session.message_count}</TableCell>
                      <TableCell className="text-xs text-text-tertiary">
                        {formatDate(session.created_at)}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => viewMessages(session.id)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Link href={`/admin/sessions/${session.id}`}>
                            <Button variant="ghost" size="sm">
                              <ExternalLink className="h-4 w-4" />
                            </Button>
                          </Link>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Messages Panel */}
        <Card className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg text-text-primary">
              {selectedSession ? "Session Messages" : "Select a Session"}
            </CardTitle>
            {selectedSession && (
              <Button variant="ghost" size="sm" onClick={closeMessages} className="text-text-tertiary hover:text-text-primary">
                <X className="h-4 w-4" />
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {!selectedSession ? (
              <p className="text-text-secondary text-center py-8">
                Click on a session to view messages
              </p>
            ) : loadingMessages ? (
              <p className="text-text-secondary text-center py-8">
                Loading messages...
              </p>
            ) : messages.length === 0 ? (
              <p className="text-text-secondary text-center py-8">
                No messages in this session
              </p>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-3 rounded-lg ${
                      msg.role === "user"
                        ? "bg-neon-cyan/10 border border-neon-cyan/30"
                        : "bg-bg-surface-3/50 border border-border-default"
                    }`}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span
                        className={`text-xs font-medium ${
                          msg.role === "user"
                            ? "text-neon-cyan"
                            : "text-text-secondary"
                        }`}
                      >
                        {msg.role === "user" ? "User" : "Assistant"}
                      </span>
                      <span className="text-xs text-text-tertiary">
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-text-primary whitespace-pre-wrap">
                      {msg.content.length > 500
                        ? msg.content.slice(0, 500) + "..."
                        : msg.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
