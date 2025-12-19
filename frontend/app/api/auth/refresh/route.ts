import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "@/lib/server-config";

export async function POST(request: NextRequest) {
  try {
    const accessToken = request.cookies.get("access_token")?.value;

    if (!accessToken) {
      return NextResponse.json(
        { detail: "Not authenticated" },
        { status: 401 }
      );
    }

    const backendUrl = getBackendUrl();

    const response = await fetch(`${backendUrl}/api/auth/refresh`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (!response.ok) {
      const res = NextResponse.json(data, { status: response.status });
      res.cookies.delete("access_token");
      return res;
    }

    const res = NextResponse.json(data);

    // Update cookie with new token if provided
    if (data.access_token) {
      res.cookies.set("access_token", data.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24,
        path: "/",
      });
    }

    return res;
  } catch (error) {
    console.error("Auth refresh proxy error:", error);
    return NextResponse.json(
      { detail: "Failed to connect to backend" },
      { status: 502 }
    );
  }
}
