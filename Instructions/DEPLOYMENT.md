# Deployment Guide

## Table of Contents
1. [Development Setup](#development-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Custom API Integration](#custom-api-integration)

---

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Quick Start

#### 1. Setup Python Backend

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or your preferred editor
```

#### 2. Setup Frontend

```bash
cd web-app

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Edit if needed (defaults work for local development)
nano .env.local
```

#### 3. Run Development Servers

```bash
# Terminal 1: Start Python backend
source .venv/bin/activate
python api_server_v2.py

# Terminal 2: Start Next.js frontend
cd web-app
npm run dev
```

Visit: http://localhost:3000

---

## Production Deployment

### Option 1: Traditional Server Deployment

#### Backend Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=false
export REALITY_DEFENDER_API_KEY=your_api_key_here
export CORS_ORIGINS=https://yourdomain.com

# Run with production server (use gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 api_server_v2:app
```

#### Frontend Deployment

```bash
cd web-app

# Set production environment
export NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Build for production
npm run build

# Start production server
npm start
```

### Option 2: Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start api_server_v2.py --name ai-detector-backend --interpreter python

# Start frontend
cd web-app
pm2 start npm --name ai-detector-frontend -- start

# Save PM2 configuration
pm2 save
pm2 startup  # Follow instructions to enable startup
```

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your API keys
nano .env

# 3. Build and start services
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop services
docker-compose down
```

### Backend Only (Docker)

```bash
# Build image
docker build -t ai-detector-backend .

# Run container
docker run -d \
  -p 5001:5001 \
  -e REALITY_DEFENDER_API_KEY=your_key \
  -e FLASK_ENV=production \
  --name ai-detector-backend \
  ai-detector-backend

# View logs
docker logs -f ai-detector-backend
```

### Full Stack (Docker Compose with Frontend)

Uncomment the frontend service in `docker-compose.yml`:

```yaml
frontend:
  build:
    context: ./web-app
    dockerfile: Dockerfile.frontend
  ports:
    - "3000:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://backend:5001
  depends_on:
    - backend
```

Then run:
```bash
docker-compose up -d
```

---

## Environment Configuration

### Backend (.env)

```env
# Required
REALITY_DEFENDER_API_KEY=your_api_key_here

# Server Configuration
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=false

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=60

# Upload Configuration
MAX_FILE_SIZE_MB=16
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,webp,bmp

# Logging
LOG_LEVEL=INFO
LOG_FILE=  # Leave empty for console only, or set path like logs/app.log

# Development/Demo Mode
ENABLE_MOCK_MODE=false  # Set true for demo without API
```

### Frontend (.env.local)

```env
# API Backend URL
NEXT_PUBLIC_API_URL=http://localhost:5001  # Development
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com  # Production

# Optional: Enable dev features
NEXT_PUBLIC_DEV_MODE=false
```

---

## Custom API Integration

### Step 1: Configure Environment

Add to `.env`:
```env
# Disable Reality Defender
REALITY_DEFENDER_API_KEY=

# Enable Custom API
CUSTOM_API_KEY=your_custom_api_key
CUSTOM_API_URL=https://api.yourservice.com
CUSTOM_API_TIMEOUT=30
```

### Step 2: Implement Custom API Service

Edit `services/custom_api.py`:

```python
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    """Implement your API logic here"""
    
    # 1. Read image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 2. Prepare request
    headers = {
        'Authorization': f'Bearer {self.api_key}',
    }
    
    files = {
        'file': (Path(image_path).name, image_data, 'image/jpeg')
    }
    
    # 3. Send request
    response = requests.post(
        f'{self.api_url}/analyze',
        headers=headers,
        files=files,
        timeout=self.timeout
    )
    response.raise_for_status()
    
    # 4. Parse response
    data = response.json()
    
    # 5. Return standardized format
    return {
        'status': 'MANIPULATED' if data['is_ai'] else 'AUTHENTIC',
        'score': float(data['confidence']),
        'confidence': self._calculate_confidence(data['confidence']),
        'metadata': data
    }
```

### Step 3: Update API Server

Edit `api_server_v2.py` line ~120:

```python
# Change from:
detector = DetectorService(
    provider='reality_defender',
    api_key=config_class.REALITY_DEFENDER_API_KEY
)

# To:
detector = DetectorService(
    provider='custom',
    api_key=config_class.CUSTOM_API_KEY,
    api_url=config_class.CUSTOM_API_URL,
    timeout=config_class.CUSTOM_API_TIMEOUT
)
```

### Step 4: Test Integration

```bash
# Start server
python api_server_v2.py

# Test endpoint
curl -X POST http://localhost:5001/api/analyze \
  -F "file=@test_image.jpg"
```

---

## Production Best Practices

### Security

1. **Use HTTPS** in production
2. **Set specific CORS origins** (not *)
3. **Use environment variables** for secrets
4. **Enable rate limiting**
5. **Use secure API keys**

### Performance

1. **Use gunicorn/uwsgi** for Python backend
2. **Enable Next.js** production mode
3. **Use CDN** for static assets
4. **Enable caching** where appropriate
5. **Monitor resource usage**

### Monitoring

1. **Setup logging** to files or service
2. **Monitor API health** endpoint: `/health`
3. **Track error rates**
4. **Set up alerts** for failures
5. **Monitor rate limits**

### Scaling

1. **Horizontal scaling**: Run multiple backend instances
2. **Load balancing**: Use nginx or cloud load balancer
3. **Database**: Add Redis for rate limiting
4. **File storage**: Use S3/cloud storage for uploads
5. **CDN**: Serve frontend via CDN

---

## Cloud Deployment Examples

### AWS (EC2 + RDS)

```bash
# 1. Launch EC2 instance
# 2. Install Docker
# 3. Clone repository
# 4. Configure .env
# 5. Run with docker-compose

docker-compose up -d

# 6. Setup nginx reverse proxy
# 7. Configure SSL with Let's Encrypt
```

### Heroku

```bash
# Backend
heroku create ai-detector-backend
heroku config:set REALITY_DEFENDER_API_KEY=your_key
git push heroku main

# Frontend (Vercel recommended)
# See Vercel section
```

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

cd web-app

# Deploy
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production
```

### Digital Ocean (Droplet)

```bash
# 1. Create droplet
# 2. SSH into droplet
# 3. Install Docker & Docker Compose
# 4. Clone repository
# 5. Configure .env
# 6. Run services

docker-compose up -d
```

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Verify dependencies: `pip install -r requirements.txt`
- Check .env file exists and has API key
- Review logs for errors

### Frontend won't connect
- Verify backend is running: `curl http://localhost:5001/health`
- Check NEXT_PUBLIC_API_URL in .env.local
- Check CORS settings in backend .env
- Review browser console for errors

### Docker issues
- Check Docker is running: `docker ps`
- Rebuild images: `docker-compose build --no-cache`
- Check logs: `docker-compose logs -f`
- Verify .env file is present

### API errors
- Check API key is valid
- Verify network connectivity
- Check rate limits
- Enable mock mode for testing: `ENABLE_MOCK_MODE=true`

---

## Support

For issues or questions:
1. Check logs for detailed error messages
2. Review configuration files
3. Test with mock mode enabled
4. Check firewall and network settings
5. Verify all environment variables are set

## Next Steps

After deployment:
1. Test all endpoints
2. Setup monitoring
3. Configure backups
4. Enable HTTPS/SSL
5. Setup CI/CD pipeline
6. Document any customizations
