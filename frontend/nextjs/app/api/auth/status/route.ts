import { NextResponse } from 'next/server';

export async function GET() {
  const backendUrl = process.env.NEXT_PUBLIC_GPTR_API_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${backendUrl}/api/auth/status`);
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('GET /api/auth/status - Error:', error);
    // If backend is unreachable, assume auth is disabled (local dev)
    return NextResponse.json({ auth_enabled: false }, { status: 200 });
  }
}
