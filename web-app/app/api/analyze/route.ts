import { NextRequest, NextResponse } from 'next/server';

// ┌─────────────────────────────────────────────────────────────────────────┐
// │ API CONFIGURATION                                                       │
// ├─────────────────────────────────────────────────────────────────────────┤
// │ This Next.js API route forwards requests to the Python backend.        │
// │                                                                         │
// │ Development: Uses http://localhost:5001                                │
// │ Production:  Set NEXT_PUBLIC_API_URL environment variable              │
// │                                                                         │
// │ TODO: Update NEXT_PUBLIC_API_URL in production deployment              │
// └─────────────────────────────────────────────────────────────────────────┘

const PYTHON_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

// Request timeout (30 seconds)
const REQUEST_TIMEOUT = 30000;

/**
 * Analyze image endpoint
 * Forwards requests to Python backend with timeout and error handling
 */
export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    // Parse form data
    const formData = await request.formData();
    const file = formData.get('file') as File;

    // Validate file
    if (!file) {
      console.warn('[API] No file provided in request');
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
      console.warn(`[API] File too large: ${file.size} bytes`);
      return NextResponse.json(
        { error: 'File too large', max_size: '16MB' },
        { status: 413 }
      );
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      console.warn(`[API] Invalid file type: ${file.type}`);
      return NextResponse.json(
        { error: 'Invalid file type', expected: 'image/*' },
        { status: 400 }
      );
    }

    // Prepare backend request
    const pythonFormData = new FormData();
    pythonFormData.append('file', file);

    const backendUrl = `${PYTHON_API_URL}/api/analyze`;
    console.log(`[API] Forwarding to backend: ${backendUrl}`);
    console.log(`[API] File: ${file.name} (${file.size} bytes, ${file.type})`);

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

      // Forward request to Python backend
      const response = await fetch(backendUrl, {
        method: 'POST',
        body: pythonFormData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const processingTime = Date.now() - startTime;
      console.log(`[API] Backend response: ${response.status} (${processingTime}ms)`);

      // Handle error responses
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
            details: errorData.details || errorData.message || 'Unknown error',
            filename: file.name
          },
          { status: response.status }
        );
      }

      // Parse successful response
      const result = await response.json();
      console.log(`[API] Analysis complete: ${result.status} (score: ${result.score?.toFixed(3)})`);
      
      // Return normalized response
      return NextResponse.json({
        status: result.status || 'UNKNOWN',
        score: result.score ?? 0,
        filename: result.filename || file.name,
        size: result.size || file.size,
        type: file.type,
        timestamp: result.timestamp || new Date().toISOString(),
        confidence: result.confidence || 'Low',
        provider: result.provider || 'unknown',
        processing_time: result.processing_time || processingTime / 1000,
        fullResult: result.fullResult || {}
      });

    } catch (error) {
      // Handle fetch errors
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
            backend_url: PYTHON_API_URL
          },
          { status: 503 }
        );
      }

      throw error;
    }

  } catch (error) {
    // Handle unexpected errors
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

// Disable Next.js body parser to handle multipart/form-data
export const config = {
  api: {
    bodyParser: false,
  },
};
