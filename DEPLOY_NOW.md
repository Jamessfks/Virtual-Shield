# 🚀 Quick Deploy to Vercel

Follow these steps to deploy Virtual Shield to Vercel in 5 minutes.

## Option 1: Deploy via GitHub (Easiest)

### Step 1: Push to GitHub
```bash
cd "/Users/jameszhao/Desktop/VIrtual Shield copy"
git add .
git commit -m "Configure for Vercel deployment"
git push origin main
```

### Step 2: Deploy on Vercel
1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select your GitHub repository
4. Click "Deploy" (Vercel auto-detects Flask)

### Step 3: Configure Environment Variables
In Vercel Dashboard → Settings → Environment Variables, add:

**For Testing (Mock Mode):**
```
FLASK_ENV = production
ENABLE_MOCK_MODE = true
```

**For Production (Real API):**
```
FLASK_ENV = production
ENABLE_MOCK_MODE = false
REALITY_DEFENDER_API_KEY = your_api_key_here
```

### Step 4: Redeploy
After adding environment variables, click "Redeploy" in the Deployments tab.

✅ Done! Your API is live at `https://your-project.vercel.app`

---

## Option 2: Deploy via CLI

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy
```bash
cd "/Users/jameszhao/Desktop/VIrtual Shield copy"
vercel
```
Follow the prompts and your app will be deployed!

---

## Testing Your Deployment

Replace `YOUR_URL` with your Vercel deployment URL:

```bash
# Health check
curl https://YOUR_URL.vercel.app/health

# API info
curl https://YOUR_URL.vercel.app/api/info

# Welcome page
curl https://YOUR_URL.vercel.app/
```

---

## What Was Configured

✅ `api/index.py` - Vercel entry point  
✅ `vercel.json` - Deployment configuration  
✅ `pyproject.toml` - Python project metadata  
✅ `.vercelignore` - Excludes unnecessary files  
✅ `VERCEL_DEPLOYMENT.md` - Full documentation  

---

## Important Notes

### Size Limit
⚠️ Vercel has a 250MB deployment limit. The configuration excludes:
- Training data (`data/`)
- Model files (`models/`)
- Upload directories
- Documentation files

### Text Detection
⚠️ Text detection requires trained model files. Options:
1. Deploy without text detection (mock mode)
2. Use external model storage (S3, Google Cloud Storage)
3. Deploy smaller models if they fit in 250MB

### Mock Mode
When `ENABLE_MOCK_MODE=true`:
- ✅ All endpoints work
- ✅ Returns mock/demo data
- ❌ No real AI detection
- 💡 Great for testing and demos!

---

## Need Help?

See `VERCEL_DEPLOYMENT.md` for detailed documentation.

Common issues:
- **Build fails**: Check Vercel function logs
- **500 errors**: Verify environment variables are set
- **Import errors**: Ensure `api_server_v2.py` is not ignored

---

## Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Set up custom domain (optional)
3. ✅ Monitor usage in Vercel dashboard
4. ✅ Set up GitHub integration for auto-deploy
5. ✅ Add real API keys for production use

Happy deploying! 🎉
