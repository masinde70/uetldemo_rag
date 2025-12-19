import { NextRequest, NextResponse } from "next/server";
import { getAdminHeaders, getBackendUrl } from "@/lib/server-config";

export async function DELETE(
  _request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  const { id } = await context.params;

  try {
    const response = await fetch(
      `${getBackendUrl()}/api/admin/documents/${id}`,
      {
        method: "DELETE",
        headers: getAdminHeaders(),
      }
    );

    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Admin delete document error:", error);
    return NextResponse.json(
      { error: "Failed to delete document" },
      { status: 500 }
    );
  }
}
