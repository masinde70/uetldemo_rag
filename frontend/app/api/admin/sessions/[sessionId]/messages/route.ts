import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl, getAdminHeaders } from "@/lib/server-config";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;
    const response = await fetch(
      `${getBackendUrl()}/api/admin/sessions/${sessionId}/messages`,
      {
        headers: getAdminHeaders(),
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch messages" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Admin messages error:", error);
    return NextResponse.json(
      { error: "Failed to connect to backend" },
      { status: 500 }
    );
  }
}
