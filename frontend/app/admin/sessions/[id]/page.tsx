"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, MessageSquare } from "lucide-react";
import { MessageViewer } from "@/components/admin/MessageViewer";
import { 
  fetchSessionMessages, 
  getModeDisplayName,
  type Message 
} from "@/lib/api";

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMessages = async () => {
      try {
        const response = await fetchSessionMessages(sessionId);
        setMessages(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch messages");
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      loadMessages();
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Loading messages...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Error: {error}</p>
        <Button 
          variant="ghost" 
          className="mt-2"
          onClick={() => router.back()}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => router.back()}
          className="text-slate-600"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <h1 className="text-2xl font-semibold text-slate-800">
          Session Details
        </h1>
      </div>

      {/* Session info */}
      <div className="mb-6 flex items-center gap-4 text-sm text-slate-500">
        <span className="font-mono bg-slate-100 px-2 py-1 rounded">
          {sessionId.slice(0, 8)}...
        </span>
        <span className="flex items-center gap-1">
          <MessageSquare className="h-4 w-4" />
          {messages.length} message{messages.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Messages */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <MessageSquare className="h-5 w-5" style={{ color: "#0033A0" }} />
            Conversation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <MessageViewer messages={messages} />
        </CardContent>
      </Card>
    </div>
  );
}
