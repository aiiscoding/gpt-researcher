import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const backendUrl = process.env.NEXT_PUBLIC_GPTR_API_URL || 'http://localhost:8000';

  try {
    const body = await request.json();

    const response = await fetch(`${backendUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    // Forward the response including set-cookie from backend
    const res = NextResponse.json(data, { status: 200 });

    // Also set cookie on the Next.js side for SSR
    if (data.token) {
      res.cookies.set('auth_token', data.token, {
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
        maxAge: 24 * 60 * 60, // 24 hours
        path: '/',
      });
    }

    return res;
  } catch (error) {
    console.error('POST /api/auth/login - Error:', error);
    return NextResponse.json({ detail: 'Failed to connect to backend' }, { status: 500 });
  }
}
