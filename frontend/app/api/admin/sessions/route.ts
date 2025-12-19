import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl, getAdminHeaders } from "@/lib/server-config";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get("limit") || "50";
    const offset = searchParams.get("offset") || "0";

    const response = await fetch(
      `${getBackendUrl()}/api/admin/sessions?limit=${limit}&offset=${offset}`,
      {
        headers: getAdminHeaders(),
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch sessions" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Admin sessions error:", error);
    return NextResponse.json(
      { error: "Failed to connect to backend" },
      { status: 500 }
    );
  }
}
