import { NextRequest, NextResponse } from 'next/server';

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';
const REQUEST_TIMEOUT = 30000;

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const body = await request.json();
    const text = body.text?.trim();

    if (!text) {
      return NextResponse.json(
        { error: 'No text provided' },
        { status: 400 }
      );
    }

    if (text.length < 10) {
      return NextResponse.json(
        { error: 'Text too short', min_length: 10 },
        { status: 400 }
      );
    }

    if (text.length > 50000) {
      return NextResponse.json(
        { error: 'Text too long', max_length: 50000 },
        { status: 413 }
      );
    }

    const backendUrl = `${BACKEND_API_URL}/api/analyze`;
    console.log(`[API] Forwarding to backend: ${backendUrl}`);
    console.log(`[API] Text length: ${text.length} characters`);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const processingTime = Date.now() - startTime;
      console.log(`[API] Backend response: ${response.status} (${processingTime}ms)`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[API] Backend error:', errorText);
        
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { error: 'Backend error', details: errorText };
        }

        return NextResponse.json(
          { 
            error: errorData.error || 'Analysis failed',
            details: errorData.details || errorData.message || 'Unknown error'
          },
          { status: response.status }
        );
      }

      const result = await response.json();
      console.log(`[API] Analysis complete: ${result.status} (score: ${result.score?.toFixed(3)})`);
      
      return NextResponse.json({
        status: result.status || 'UNKNOWN',
        score: result.score ?? 0,
        text_length: result.text_length || text.length,
        timestamp: result.timestamp || new Date().toISOString(),
        confidence: result.confidence || 'Low',
        provider: result.provider || 'unknown',
        processing_time: result.processing_time || processingTime / 1000,
        fullResult: result.fullResult || {}
      });

    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          console.error('[API] Request timeout');
          return NextResponse.json(
            { 
              error: 'Request timeout',
              details: `Request took longer than ${REQUEST_TIMEOUT / 1000} seconds`
            },
            { status: 504 }
          );
        }
        
        console.error('[API] Network error:', error.message);
        return NextResponse.json(
          { 
            error: 'Network error',
            details: `Failed to connect to backend: ${error.message}`,
            backend_url: BACKEND_API_URL
          },
          { status: 503 }
        );
      }

      throw error;
    }

  } catch (error) {
    console.error('[API] Unexpected error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
