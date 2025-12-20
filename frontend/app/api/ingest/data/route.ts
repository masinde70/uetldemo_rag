import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "@/lib/server-config";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const backendUrl = getBackendUrl();

    const response = await fetch(`${backendUrl}/api/ingest/data`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Ingest data proxy error:", error);
    return NextResponse.json(
      { detail: "Failed to connect to backend" },
      { status: 502 }
    );
  }
}
