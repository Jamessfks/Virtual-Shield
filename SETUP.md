# AI Screenshot Detector - Setup & Commands

## Quick Start (Automated)

### Make the startup script executable and run it:

```bash
chmod +x start_servers.sh
./start_servers.sh
```

This will start both servers automatically. Press `Ctrl+C` to stop both.

---

## Manual Setup (Step by Step)

### Prerequisites

1. **Python 3.x** installed
2. **Node.js 18+** and **npm** installed
3. Virtual environment set up (if not already done)

### First Time Setup

#### 1. Install Python Dependencies

```bash
# From project root directory
cd "/Users/jameszhao/Desktop/VIrtual Shield copy"

# Activate virtual environment
source .venv/bin/activate

# Install required packages
pip install Flask Flask-CORS realitydefender Werkzeug
```

#### 2. Install Node.js Dependencies

```bash
# Navigate to web app directory
cd web-app

# Install dependencies
npm install

# Return to project root
cd ..
```

---

## Running the Application

### Option 1: Run Both Servers Separately (RECOMMENDED)

#### Terminal 1 - Python Backend

```bash
# Navigate to project root
cd "/Users/jameszhao/Desktop/VIrtual Shield copy"

# Activate virtual environment
source .venv/bin/activate

# Start Python API server
python api_server.py
```

**Output:** Server running on `http://localhost:5001`

#### Terminal 2 - Next.js Frontend

```bash
# Navigate to web app directory
cd "/Users/jameszhao/Desktop/VIrtual Shield copy/web-app"

# Start Next.js development server
npm run dev
```

**Output:** Application running on `http://localhost:3000`

#### Open Browser

Visit: **http://localhost:3000**

---

### Option 2: Use Startup Script

```bash
cd "/Users/jameszhao/Desktop/VIrtual Shield copy"
chmod +x start_servers.sh
./start_servers.sh
```

---

## Stopping the Servers

### If running separately:
- Press `Ctrl+C` in each terminal window

### If using startup script:
- Press `Ctrl+C` once (stops both servers)

### Force kill if needed:
```bash
# Kill Python server
lsof -ti:5001 | xargs kill -9

# Kill Next.js server
lsof -ti:3000 | xargs kill -9
```

---

## Troubleshooting

### Port Already in Use

#### Port 5001 (Python Backend)
```bash
# Find process using port 5001
lsof -ti:5001

# Kill the process
lsof -ti:5001 | xargs kill -9

# Restart Python server
source .venv/bin/activate && python api_server.py
```

#### Port 3000 (Next.js Frontend)
```bash
# Find process using port 3000
lsof -ti:3000

# Kill the process
lsof -ti:3000 | xargs kill -9

# Restart Next.js server
cd web-app && npm run dev
```

### Reality Defender Connection Issues

If you see errors about Reality Defender:
1. Check your internet connection
2. Verify API key in `api_server.py` (line 36)
3. Check Reality Defender API status

### Module Not Found Errors

```bash
# Python modules
source .venv/bin/activate
pip install -r requirements.txt

# Node modules
cd web-app
rm -rf node_modules package-lock.json
npm install
```

---

## Commands Reference

### Python Backend Commands

```bash
# Start server
python api_server.py

# Test if server is running
curl http://localhost:5001/health

# Test endpoint
curl http://localhost:5001/api/test
```

### Next.js Frontend Commands

```bash
# Development mode
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

---

## Server Status Check

### Check if servers are running:

```bash
# Check Python backend
curl http://localhost:5001/health

# Check Next.js frontend (should return HTML)
curl http://localhost:3000
```

### View server logs:

- **Python**: Logs appear in the terminal where you ran `python api_server.py`
- **Next.js**: Logs appear in the terminal where you ran `npm run dev`

---

## File Locations

- **Python Backend**: `/Users/jameszhao/Desktop/VIrtual Shield copy/api_server.py`
- **Web App**: `/Users/jameszhao/Desktop/VIrtual Shield copy/web-app/`
- **Upload Folder**: `/Users/jameszhao/Desktop/VIrtual Shield copy/uploads/`
- **Logs**: Terminal output (stdout/stderr)

---

## Important Notes

1. **Always start Python backend FIRST**, then the Next.js frontend
2. Both servers must be running for the application to work
3. The application will continue running until you stop it with `Ctrl+C`
4. Uploaded images are temporarily saved in `uploads/` folder and deleted after analysis
5. Python server now runs with threading enabled for better concurrent request handling
6. Debug mode is disabled for stability

---

## System Requirements

- **macOS** (tested)
- **Python 3.8+**
- **Node.js 18+**
- **4GB RAM minimum**
- **Internet connection** (for Reality Defender API)

---

## Support

If servers stop unexpectedly:
1. Check terminal output for error messages
2. Restart both servers
3. Check port availability
4. Verify all dependencies are installed
