import { NextRequest, NextResponse } from 'next/server';

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:5001';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Forward the request to Python backend
    const pythonFormData = new FormData();
    pythonFormData.append('file', file);

    console.log('Forwarding request to Python backend:', `${PYTHON_API_URL}/api/analyze`);

    try {
      const response = await fetch(`${PYTHON_API_URL}/api/analyze`, {
        method: 'POST',
        body: pythonFormData,
      });

      console.log('Python backend response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Python backend error response:', errorText);
        try {
          const errorData = JSON.parse(errorText);
          console.error('Python backend error data:', errorData);
          return NextResponse.json(
            { 
              error: 'Analysis failed',
              details: errorData.error || errorData.details || 'Unknown error',
              filename: file.name
            },
            { status: response.status }
          );
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
          return NextResponse.json(
            { 
              error: 'Analysis failed',
              details: errorText || 'Python backend error'
            },
            { status: response.status }
          );
        }
      }

      const result = await response.json();
      console.log('Analysis result received:', result);
      
      // Return the result from Python backend
      return NextResponse.json({
        status: result.status || 'UNKNOWN',
        score: result.score || 0,
        filename: result.filename || file.name,
        size: result.size || file.size,
        type: file.type,
        timestamp: result.timestamp || new Date().toISOString(),
        confidence: result.confidence,
        fullResult: result.fullResult
      });

    } catch (error) {
      console.error('Network error calling Python backend:', error);
      return NextResponse.json(
        { 
          error: 'Network error',
          details: error instanceof Error ? error.message : 'Failed to connect to Python backend'
        },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error in API route:', error);
    return NextResponse.json(
      { 
        error: 'Internal Server Error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export const config = {
  api: {
    bodyParser: false,
  },
};
