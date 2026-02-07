import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const backendUrl = process.env.NEXT_PUBLIC_GPTR_API_URL || 'http://localhost:8000';

  try {
    const authHeader = request.headers.get('authorization') || '';

    const response = await fetch(`${backendUrl}/api/auth/me`, {
      headers: {
        Authorization: authHeader,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('GET /api/auth/me - Error:', error);
    return NextResponse.json({ detail: 'Failed to connect to backend' }, { status: 500 });
  }
}
