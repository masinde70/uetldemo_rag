import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "@/lib/server-config";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const backendUrl = getBackendUrl();

    const response = await fetch(`${backendUrl}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    // Create response with the data
    const res = NextResponse.json(data);

    // If backend returns a token, set it as HttpOnly cookie
    if (data.access_token) {
      res.cookies.set("access_token", data.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24, // 24 hours
        path: "/",
      });
    }

    return res;
  } catch (error) {
    console.error("Login proxy error:", error);
    return NextResponse.json(
      { detail: "Failed to connect to backend" },
      { status: 502 }
    );
  }
}
