import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

/**
 * Streaming chat API route - proxies SSE from backend to frontend.
 *
 * This route handles Server-Sent Events (SSE) streaming, forwarding
 * tokens from the FastAPI backend as they are generated.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Get user email from header or use default
    const userEmail =
      request.headers.get("x-user-email") || "demo@uetcl.go.ug";

    // Make request to backend streaming endpoint
    const response = await fetch(`${BACKEND_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Email": userEmail,
        Accept: "text/event-stream",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      return new Response(
        JSON.stringify({ error: error.detail || "Backend request failed" }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Check if we got a streaming response
    if (!response.body) {
      return new Response(
        JSON.stringify({ error: "No response body from backend" }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Create a TransformStream to pass through the SSE data
    const { readable, writable } = new TransformStream();

    // Pipe the backend response through to the client
    const writer = writable.getWriter();
    const reader = response.body.getReader();

    // Start piping in the background
    (async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            await writer.close();
            break;
          }
          await writer.write(value);
        }
      } catch (error) {
        console.error("Stream error:", error);
        await writer.abort(error);
      }
    })();

    // Return the readable stream with SSE headers
    return new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    console.error("Chat stream API error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to connect to backend" }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

// Disable body parsing for streaming
export const runtime = "edge";
