# AI Screenshot Detector

A minimalist black and white web application for detecting AI-generated content in images using Reality Defender API. Features a clean, bold design with Montserrat typography and a Python Flask backend.

## Architecture

- **Frontend**: Next.js 14 + React + TypeScript + TailwindCSS
- **Backend**: Python Flask API with Reality Defender integration + fallback mock
- **Design**: Minimalistic black & white with bold Montserrat font

## Features

- **Minimalist Design** - Clean black and white interface with bold typography
- **Drag & Drop Upload** - Easy image upload with drag and drop support
- **Python Backend** - Flask API server leveraging Reality Defender
- **Real-time Analysis** - Instant AI detection results
- **Results History** - Track all analyzed images with detailed metrics
- **Export Results** - Download analysis history as JSON
- **Fallback Mode** - Works with mock responses when Reality Defender API is unavailable

## Quick Start

### 1. Start Python Backend (Required)

```bash
# From project root directory
source .venv/bin/activate
python api_server.py
```

The Python API will start on **http://localhost:5001**

### 2. Start Web Application

```bash
# Navigate to web-app directory
cd web-app

# Start Next.js development server
npm run dev
```

The web app will start on **http://localhost:3000**

### 3. Access Application

Open your browser and visit: **http://localhost:3000**

## Project Structure

```
VIrtual Shield/
├── api_server.py              # Python Flask API backend
├── ai_screenshot_detector.py  # Original desktop application
├── requirements.txt           # Python dependencies
├── uploads/                   # Temporary upload folder
└── web-app/                   # Next.js web application
    ├── app/
    │   ├── api/analyze/
    │   │   └── route.ts       # Next.js API route (forwards to Python)
    │   ├── globals.css        # Black & white theme
    │   ├── layout.tsx         # Root layout with Montserrat
    │   └── page.tsx           # Main UI component
    ├── components/ui/         # Reusable UI components
    ├── lib/utils.ts           # Utility functions
    └── package.json           # Node dependencies
```

## API Behavior

### Reality Defender API Status
- **Available**: Uses real AI detection analysis
- **Unavailable** (service down, network issues): Automatically falls back to **mock responses** for demo purposes

The application will work in both cases - with real analysis when the API is available, and with simulated results when it's not.

## API Endpoints

### Python Flask API (Port 5001)

- `GET /health` - Health check endpoint
- `POST /api/analyze` - Analyze image for AI content
- `GET /api/test` - Test endpoint

### Next.js API (Port 3000)

- `POST /api/analyze` - Proxy endpoint that forwards to Python backend

## Environment Variables

### Web Application

Create `.env.local` in `web-app/` directory:

```env
PYTHON_API_URL=http://localhost:5001
```

## Design System

### Colors
- **Primary**: Pure Black (`#000000`)
- **Background**: Pure White (`#FFFFFF`)
- **Borders**: Black (`#000000`)
- **Text**: Black on White

### Typography
- **Font**: Montserrat
- **Weights**: 400 (Regular), 600 (SemiBold), 700 (Bold), 800 (ExtraBold), 900 (Black)
- **Style**: ALL CAPS for headings and buttons

### Components
- **Borders**: 2px solid black
- **Buttons**: Black background with white text, bold uppercase
- **Cards**: White background with 2px black border, no shadows
- **Status Badges**: Black border, inverted colors for AI detected

## Detection Results

- **AI DETECTED** - Image is AI-generated (MANIPULATED status)
- **AUTHENTIC** - Image appears authentic
- **AI Score** - Numerical score 0-1 indicating AI likelihood
- **Confidence** - High/Medium/Low based on score

## Development

### Install Python Dependencies

```bash
pip install Flask Flask-CORS realitydefender Werkzeug
```

### Install Node Dependencies

```bash
cd web-app
npm install
```

### Build for Production

```bash
cd web-app
npm run build
npm start
```

## Important Notes

1. **Always start Python backend FIRST**, then the Next.js frontend
2. Both servers must be running for the application to work
3. The application will continue running until you stop it with `Ctrl+C`
4. Uploaded images are temporarily saved in `uploads/` folder and deleted after analysis
5. Python server now runs with threading enabled for better concurrent request handling
6. Debug mode is disabled for stability
7. **Automatic fallback to mock responses** when Reality Defender API is unavailable

## Troubleshooting

### Port 5000 Already in Use
macOS AirPlay Receiver uses port 5000. The Python server uses port 5001 instead.

### Python Backend Not Running
Make sure to start the Python API server before using the web application:
```bash
source .venv/bin/activate
python api_server.py
```

### Reality Defender Connection Issues

If you see errors about Reality Defender:
1. Check your internet connection
2. Verify API key in `api_server.py` (line 36)
3. Check Reality Defender API status

**Note**: The application includes automatic fallback to mock responses when the API is unavailable.

## Support

If servers stop unexpectedly:
1. Check terminal output for error messages
2. Restart both servers
3. Check port availability
4. Verify all dependencies are installed

**The application includes automatic fallback functionality and will work even when the Reality Defender API is unavailable.**

## License

This project uses Reality Defender API for AI detection.
