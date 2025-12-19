import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

/**
 * Proxy for detailed health check endpoint.
 *
 * Returns service status and capability flags for graceful degradation.
 */
export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health/detailed`, {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      // Return degraded status if backend is unreachable
      return NextResponse.json(
        {
          status: "unhealthy",
          timestamp: new Date().toISOString(),
          services: {
            database: { status: "unhealthy", latency_ms: null, message: "Backend unavailable" },
            qdrant: { status: "unhealthy", latency_ms: null, message: "Backend unavailable" },
            openai: { status: "unhealthy", latency_ms: null, message: "Backend unavailable" },
          },
          capabilities: {
            chat: false,
            streaming: false,
            session_history: false,
            document_retrieval: false,
            analytics: false,
            admin: false,
            file_upload: false,
          },
        },
        { status: 200 } // Return 200 with unhealthy status so frontend can handle gracefully
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Health check error:", error);

    // Return offline-like status
    return NextResponse.json(
      {
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        services: {
          database: { status: "unhealthy", latency_ms: null, message: "Connection failed" },
          qdrant: { status: "unhealthy", latency_ms: null, message: "Connection failed" },
          openai: { status: "unhealthy", latency_ms: null, message: "Connection failed" },
        },
        capabilities: {
          chat: false,
          streaming: false,
          session_history: false,
          document_retrieval: false,
          analytics: false,
          admin: false,
          file_upload: false,
        },
      },
      { status: 200 }
    );
  }
}
