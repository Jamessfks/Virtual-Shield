# AI Screenshot Detector - Production Ready

A production-grade web application for detecting AI-generated content in images. Features a modular architecture with support for custom AI detection APIs, comprehensive error handling, and deployment-ready configuration.

## ✨ Key Features

- **🎨 Clean Design**: Minimalist black & white interface with bold Montserrat typography
- **🔌 Modular API**: Easy integration with any AI detection service
- **🚀 Production Ready**: Docker, environment configs, and deployment guides included
- **📊 Real-time Analysis**: Instant AI detection results with confidence scores
- **📈 Results History**: Track and export analysis history
- **🛡️ Secure**: Rate limiting, CORS, input validation, and error handling
- **🎯 Fallback Support**: Mock mode for development and testing

## Architecture

```
┌──────────────────┐
│  Next.js 14     │  TypeScript + TailwindCSS
│  Frontend       │  Modern React Components
└────────┬─────────┘
         │ REST API
         ▼
┌──────────────────┐
│  Flask API      │  Python 3.11+
│  Server v2.0    │  Production-grade backend
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Detector        │  Abstraction Layer
│ Service         │  Multi-provider support
└────────┬─────────┘
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌──────┐ ┌──────┐
│Reality  │ │Custom  │ │ Mock │ │Future│
│Defender │ │  API   │ │ Mode │ │ APIs │
└─────────┘ └────────┘ └──────┘ └──────┘
```

### Technology Stack

- **Frontend**: Next.js 14 + React 18 + TypeScript + TailwindCSS
- **Backend**: Python 3.11 + Flask 3.0 + Environment-based config
- **AI Detection**: Reality Defender API (default) + Custom API support
- **Deployment**: Docker + Docker Compose ready
- **Design**: Minimalistic black & white with Montserrat font

## 🚀 Production Improvements (v2.0)

### Backend Enhancements
- ✅ **Environment Configuration**: `.env` file support with validation
- ✅ **Modular Architecture**: Service-based design for easy API swapping
- ✅ **Custom API Ready**: Plug-and-play integration for your AI detection API
- ✅ **Rate Limiting**: Built-in request throttling (60/min default)
- ✅ **Enhanced Logging**: Structured logging with configurable levels
- ✅ **Error Handling**: Comprehensive exception handling and user-friendly errors
- ✅ **Input Validation**: File type, size, and format validation
- ✅ **Health Checks**: `/health` endpoint for monitoring

### Frontend Enhancements
- ✅ **Request Timeout**: 30-second timeout with proper error messages
- ✅ **File Validation**: Client-side validation before upload
- ✅ **Better Error Messages**: Clear, actionable error feedback
- ✅ **Loading States**: Enhanced UX during analysis
- ✅ **Type Safety**: Full TypeScript coverage

### DevOps & Deployment
- ✅ **Docker Support**: Dockerfile and docker-compose.yml included
- ✅ **Environment Templates**: `.env.example` with all options documented
- ✅ **Production Config**: Gunicorn-ready, optimized for deployment
- ✅ **Documentation**: Comprehensive deployment and integration guides
- ✅ **CI/CD Ready**: Structured for automated deployments

## Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# 1. Clone repository
git clone <repository-url>
cd "VIrtual Shield copy"

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API key

# 3. Start services
docker-compose up -d

# 4. Access application
# Visit http://localhost:3000
```

### Option 2: Local Development

#### Backend Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set:
#   REALITY_DEFENDER_API_KEY=your_key_here
# OR
#   ENABLE_MOCK_MODE=true  # for testing without API

# 4. Start server (Production version)
python api_server_v2.py
```

Backend runs on: **http://localhost:5001**

#### Frontend Setup

```bash
# 1. Navigate to web-app
cd web-app

# 2. Install dependencies
npm install

# 3. Configure environment (optional)
cp .env.local.example .env.local
# Default NEXT_PUBLIC_API_URL=http://localhost:5001 works for local dev

# 4. Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

### Option 3: Quick Test (Mock Mode)

```bash
# Test without API key
export ENABLE_MOCK_MODE=true
python api_server_v2.py

# In another terminal
cd web-app && npm run dev
```

## 📁 Project Structure

```
Virtual Shield/
├── 📄 Configuration Files
│   ├── .env.example                # Environment template
│   ├── config.py                   # Python configuration management
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend container
│   ├── docker-compose.yml          # Full stack deployment
│   └── .dockerignore              # Docker ignore rules
│
├── 🔧 Backend (Python Flask)
│   ├── api_server_v2.py           # Production API server ⭐ NEW
│   ├── api_server.py              # Legacy server
│   └── services/                  # Service layer ⭐ NEW
│       ├── __init__.py
│       ├── detector.py            # Unified detector interface
│       └── custom_api.py          # Custom API integration template
│
├── 🌐 Frontend (Next.js)
│   └── web-app/
│       ├── app/
│       │   ├── api/analyze/
│       │   │   └── route.ts       # Enhanced API route ⭐ IMPROVED
│       │   ├── globals.css
│       │   ├── layout.tsx
│       │   └── page.tsx
│       ├── components/ui/
│       ├── lib/utils.ts
│       ├── next.config.js         # Enhanced config ⭐ IMPROVED
│       ├── Dockerfile.frontend    # Frontend container ⭐ NEW
│       ├── .env.local.example     # Frontend env template ⭐ NEW
│       └── package.json
│
├── 📚 Documentation
│   ├── README.md                  # This file (updated)
│   ├── DEPLOYMENT.md              # Deployment guide ⭐ NEW
│   ├── API_INTEGRATION_GUIDE.md   # Custom API guide ⭐ NEW
│   └── SETUP.md                   # Original setup guide
│
└── 🗂️ Other
    ├── uploads/                   # Temporary files
    ├── screenshots/               # Sample images
    └── ai_screenshot_detector.py  # Original desktop app
```

## 🔌 Custom API Integration

### Ready for Your API

The application is designed for easy integration with **your custom AI detection API**:

```python
# services/custom_api.py - Ready for your implementation
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    # TODO: Implement your API integration here
    # See detailed instructions in the file and API_INTEGRATION_GUIDE.md
```

### Quick Integration Steps

1. **Configure** your API credentials in `.env`:
   ```env
   CUSTOM_API_KEY=your_api_key
   CUSTOM_API_URL=https://api.yourservice.com
   ```

2. **Implement** the `analyze_image()` method in `services/custom_api.py`

3. **Switch** provider in `api_server_v2.py` (line ~120):
   ```python
   detector = DetectorService(
       provider='custom',
       api_key=config.CUSTOM_API_KEY,
       api_url=config.CUSTOM_API_URL
   )
   ```

4. **Test** your integration:
   ```bash
   python api_server_v2.py
   ```

📖 **Full Guide**: See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) for detailed instructions and examples.

### Supported Modes

- **Reality Defender** (default): Production AI detection
- **Custom API**: Your own AI detection service
- **Mock Mode**: Development and testing without API

## 🔗 API Endpoints

### Python Flask API (Port 5001)

#### `GET /health`
Health check with system status
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "detector": {
    "healthy": true,
    "provider": "reality_defender",
    "mode": "production"
  },
  "timestamp": "2024-11-02T17:26:00Z"
}
```

#### `POST /api/analyze`
Analyze image for AI content

**Request:**
```bash
curl -X POST http://localhost:5001/api/analyze \
  -F "file=@image.jpg"
```

**Response:**
```json
{
  "success": true,
  "filename": "image.jpg",
  "status": "MANIPULATED",
  "score": 0.857,
  "confidence": "High",
  "provider": "reality_defender",
  "processing_time": 1.234,
  "timestamp": "2024-11-02T17:26:00Z"
}
```

#### `GET /api/info`
API information and documentation

### Next.js API (Port 3000)

#### `POST /api/analyze`
Proxy endpoint that forwards to Python backend with:
- Request validation
- Timeout handling (30s)
- Enhanced error messages

## ⚙️ Environment Configuration

### Backend (.env)

```env
# ==================================
# REQUIRED
# ==================================
REALITY_DEFENDER_API_KEY=your_api_key_here

# ==================================
# CUSTOM API (Optional)
# ==================================
# CUSTOM_API_KEY=your_custom_api_key
# CUSTOM_API_URL=https://api.yourservice.com
# CUSTOM_API_TIMEOUT=30

# ==================================
# SERVER
# ==================================
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=false

# ==================================
# SECURITY
# ==================================
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_PER_MINUTE=60

# ==================================
# FEATURES
# ==================================
ENABLE_MOCK_MODE=false  # true for development
MAX_FILE_SIZE_MB=16
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
# API Backend URL
NEXT_PUBLIC_API_URL=http://localhost:5001

# Development mode
NEXT_PUBLIC_DEV_MODE=false
```

See `.env.example` for full configuration options.

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

## 🛠️ Development

### Python Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest black mypy

# Run with auto-reload (for development)
export FLASK_ENV=development
python api_server_v2.py

# Run tests
pytest tests/

# Format code
black .

# Type checking
mypy .
```

### Frontend Development

```bash
cd web-app

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint
npm run lint
```

### Using Mock Mode

```bash
# Test without API key
export ENABLE_MOCK_MODE=true
python api_server_v2.py
```

Mock mode generates random detection results for testing.

## 📦 Deployment

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guides:
- Traditional server deployment
- Docker deployment
- Cloud deployment (AWS, Hercel, Vercel, Digital Ocean)
- Nginx configuration
- SSL/HTTPS setup
- CI/CD pipelines

### Environment-Specific Configs

```bash
# Development
export FLASK_ENV=development
python api_server_v2.py

# Production
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5001 api_server_v2:app
```

## 🐛 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version (need 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Verify .env file exists
ls -la .env

# Check logs for errors
python api_server_v2.py
```

#### Frontend can't connect to backend
```bash
# Test backend health
curl http://localhost:5001/health

# Check environment variable
echo $NEXT_PUBLIC_API_URL

# Verify CORS settings in backend .env
cat .env | grep CORS
```

#### Docker issues
```bash
# Rebuild containers
docker-compose build --no-cache

# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

#### API Integration Issues
- Check API key is valid and not expired
- Verify API endpoint URL is correct
- Test with mock mode first: `ENABLE_MOCK_MODE=true`
- Review logs for detailed error messages
- See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)

### Getting Help

1. Check logs for error messages
2. Review relevant documentation:
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment issues
   - [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) - API issues
3. Test with mock mode to isolate issues
4. Verify all environment variables are set

## 📝 Important Notes

1. **Production Ready**: `api_server_v2.py` is the production-grade server
2. **Legacy Server**: `api_server.py` is kept for backward compatibility
3. **Auto Cleanup**: Uploaded files are automatically deleted after analysis
4. **Rate Limiting**: Default 60 requests/minute (configurable)
5. **Mock Mode**: Available for development without API key
6. **Custom API**: Ready for integration with detailed guides
7. **Security**: Input validation, CORS, rate limiting included
8. **Monitoring**: Health check endpoint for production monitoring

## 📚 Documentation

- **[README.md](README.md)** - This file (overview and quick start)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **[API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)** - Custom API integration
- **[SETUP.md](SETUP.md)** - Original setup instructions

## 🆕 What's New in v2.0

### Backend
- ✅ Modular service architecture
- ✅ Environment-based configuration
- ✅ Custom API integration support
- ✅ Enhanced error handling
- ✅ Rate limiting
- ✅ Structured logging
- ✅ Health check endpoint

### Frontend
- ✅ Request timeout handling
- ✅ Better error messages
- ✅ Client-side validation
- ✅ Loading state improvements

### DevOps
- ✅ Docker support
- ✅ Docker Compose configuration
- ✅ Environment templates
- ✅ Production documentation
- ✅ Deployment guides

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional AI detection providers
- Enhanced frontend features
- Performance optimizations
- Documentation improvements
- Test coverage

## 📄 License

This project uses Reality Defender API for AI detection. Custom API integration supported.

## 🙏 Acknowledgments

- Reality Defender for AI detection API
- Next.js and React teams
- Flask and Python community
