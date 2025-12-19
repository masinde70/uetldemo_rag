import { NextResponse } from "next/server";
import { getBackendUrl, getAdminHeaders } from "@/lib/server-config";

export async function GET() {
  try {
    const response = await fetch(`${getBackendUrl()}/api/admin/analytics`, {
      headers: getAdminHeaders(),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch analytics" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Admin analytics error:", error);
    return NextResponse.json(
      { error: "Failed to connect to backend" },
      { status: 500 }
    );
  }
}
