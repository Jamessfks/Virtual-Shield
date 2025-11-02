# Migration Guide: v1.0 → v2.0

This guide helps you migrate from the original implementation to the production-ready v2.0.

---

## What's Changed

### New Files (v2.0)
- `api_server_v2.py` - Production API server
- `config.py` - Environment configuration
- `services/` - Service layer architecture
- `.env.example` - Environment template
- `Dockerfile` & `docker-compose.yml` - Container configs
- `DEPLOYMENT.md` - Deployment guide
- `API_INTEGRATION_GUIDE.md` - Custom API integration

### Modified Files
- `requirements.txt` - Added `python-dotenv`
- `web-app/app/api/analyze/route.ts` - Enhanced error handling
- `web-app/next.config.js` - Production optimizations
- `.gitignore` - Fixed to allow web-app/lib/
- `README.md` - Comprehensive update

### Deprecated (But Still Available)
- `api_server.py` - Legacy server (use `api_server_v2.py`)

---

## Migration Steps

### 1. Update Dependencies

```bash
# Backend
pip install -r requirements.txt  # Adds python-dotenv

# Frontend (no changes needed)
cd web-app
npm install
```

### 2. Create Environment Configuration

```bash
# Copy template
cp .env.example .env

# Edit and add your API key
nano .env
```

Set at minimum:
```env
REALITY_DEFENDER_API_KEY=your_api_key_here
```

### 3. Switch to New Server

**Old way:**
```bash
python api_server.py
```

**New way:**
```bash
python api_server_v2.py
```

### 4. Update Frontend Environment (Optional)

```bash
cd web-app
cp .env.local.example .env.local
```

Default values work for local development.

### 5. Test the Migration

```bash
# Start new backend
python api_server_v2.py

# In another terminal, start frontend
cd web-app
npm run dev

# Visit http://localhost:3000
```

---

## Configuration Comparison

### Old (Hardcoded)
```python
# api_server.py
API_KEY = "rd_d3d3eac041426e52_1cb3a26dc710d98f1603883f38e51753"  # Hardcoded!
UPLOAD_FOLDER = Path('uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
```

### New (Environment-based)
```python
# api_server_v2.py + config.py
from config import Config

# Values loaded from .env
Config.REALITY_DEFENDER_API_KEY
Config.UPLOAD_FOLDER
Config.MAX_CONTENT_LENGTH
```

---

## API Changes

### Endpoints

All existing endpoints work the same:
- `GET /health` ✅ (Enhanced with more info)
- `POST /api/analyze` ✅ (Same interface, better error handling)
- `GET /api/test` → `GET /api/info` (Renamed for clarity)

### Response Format

**No breaking changes!** Responses are backward compatible.

New fields added (optional):
```json
{
  "success": true,
  "filename": "image.jpg",
  "status": "MANIPULATED",
  "score": 0.857,
  "confidence": "High",
  "timestamp": "2024-11-02T17:26:00Z",
  
  // NEW in v2.0 (optional)
  "provider": "reality_defender",
  "processing_time": 1.234
}
```

---

## Feature Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **Reality Defender API** | ✅ | ✅ |
| **Mock Mode** | ✅ | ✅ Enhanced |
| **Custom API Support** | ❌ | ✅ Ready |
| **Environment Config** | ❌ | ✅ Full |
| **Rate Limiting** | ❌ | ✅ Built-in |
| **Error Handling** | Basic | ✅ Comprehensive |
| **Input Validation** | Basic | ✅ Enhanced |
| **Health Checks** | Basic | ✅ Detailed |
| **Logging** | Basic | ✅ Structured |
| **Docker Support** | ❌ | ✅ Full |
| **Production Docs** | ❌ | ✅ Complete |

---

## Breaking Changes

### None! 

v2.0 is fully backward compatible. You can:
- Keep using `api_server.py` (not recommended)
- Switch to `api_server_v2.py` (recommended)
- Frontend code works with both servers

---

## Rollback Plan

If you need to rollback:

```bash
# 1. Keep using old server
python api_server.py

# 2. Remove new files (optional)
rm api_server_v2.py config.py .env.example
rm -rf services/

# 3. Restore original requirements.txt (optional)
git checkout requirements.txt
```

---

## Production Deployment Migration

### Old Deployment
```bash
# Manual process
python api_server.py &
cd web-app
npm run build
npm start &
```

### New Deployment Options

**Option 1: Docker (Recommended)**
```bash
docker-compose up -d
```

**Option 2: Traditional**
```bash
# Backend with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 api_server_v2:app

# Frontend
cd web-app
npm run build
npm start
```

**Option 3: PM2**
```bash
pm2 start api_server_v2.py --interpreter python
cd web-app
pm2 start npm --name frontend -- start
```

---

## Environment Variables Migration

### Step 1: Extract Current Config

From `api_server.py`, note:
- API_KEY (line 36)
- UPLOAD_FOLDER (line 28)
- Any custom settings

### Step 2: Create .env

```env
REALITY_DEFENDER_API_KEY=<your_api_key_from_line_36>
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=16
FLASK_ENV=production
FLASK_PORT=5001
```

### Step 3: Remove Hardcoded Values

Your API key is now in `.env` (never committed to git).

---

## Testing Checklist

After migration, test:

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Image upload works
- [ ] Analysis returns results
- [ ] Results history displays
- [ ] Export function works
- [ ] Health endpoint responds
- [ ] Error messages display properly
- [ ] Mock mode works (if used)

---

## Benefits of v2.0

1. **Security**: API keys in environment, not code
2. **Flexibility**: Easy to switch AI providers
3. **Production-Ready**: Docker, monitoring, rate limiting
4. **Maintainability**: Modular architecture
5. **Documentation**: Comprehensive guides
6. **Developer Experience**: Mock mode, better errors
7. **Deployment**: Multiple options with guides

---

## Need Help?

- **Documentation**: See `README.md`, `DEPLOYMENT.md`, `API_INTEGRATION_GUIDE.md`
- **Issues**: Check logs for detailed error messages
- **Rollback**: Use old `api_server.py` if needed
- **Testing**: Use mock mode: `ENABLE_MOCK_MODE=true`

---

## Next Steps

1. ✅ Migrate to v2.0 server
2. ✅ Set up environment configuration
3. ✅ Test thoroughly
4. ⏭️ Consider Docker deployment
5. ⏭️ Plan custom API integration (if needed)
6. ⏭️ Setup production monitoring
7. ⏭️ Configure CI/CD pipeline

---

## Summary

**Migration is simple and safe:**
- Install new dependency: `pip install python-dotenv`
- Create `.env` file with your API key
- Run `api_server_v2.py` instead of `api_server.py`
- Everything else works the same!

**Recommended timeline:**
- Development: Immediate (no risk)
- Staging: Test for 1-2 days
- Production: Deploy when confident
