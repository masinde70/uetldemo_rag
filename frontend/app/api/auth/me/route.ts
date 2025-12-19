import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "@/lib/server-config";

export async function GET(request: NextRequest) {
  try {
    const accessToken = request.cookies.get("access_token")?.value;

    if (!accessToken) {
      return NextResponse.json(
        { detail: "Not authenticated" },
        { status: 401 }
      );
    }

    const backendUrl = getBackendUrl();

    const response = await fetch(`${backendUrl}/api/auth/me`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (!response.ok) {
      // Clear invalid token
      const res = NextResponse.json(data, { status: response.status });
      res.cookies.delete("access_token");
      return res;
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Auth me proxy error:", error);
    return NextResponse.json(
      { detail: "Failed to connect to backend" },
      { status: 502 }
    );
  }
}
