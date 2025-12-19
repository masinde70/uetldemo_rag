import { NextResponse } from "next/server";

export async function GET() {
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

  try {
    const res = await fetch(`${backendUrl}/api/health`, {
      cache: "no-store",
    });

    if (!res.ok) {
      return NextResponse.json(
        { status: "error", message: `Backend returned ${res.status}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Backend unreachable";
    return NextResponse.json({ status: "error", message }, { status: 503 });
  }
}
