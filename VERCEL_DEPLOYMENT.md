# Deploying Virtual Shield to Vercel

This guide explains how to deploy the Virtual Shield API to Vercel.

## Prerequisites

1. [Vercel Account](https://vercel.com/signup) (free)
2. [Vercel CLI](https://vercel.com/cli) installed (optional, for CLI deployment)

## Deployment Methods

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the Flask configuration

3. **Configure Environment Variables**
   In the Vercel dashboard, add these environment variables:
   - `FLASK_ENV` = `production`
   - `ENABLE_MOCK_MODE` = `true` (or false if you have API keys)
   - `REALITY_DEFENDER_API_KEY` = `your-api-key` (if not using mock mode)
   - `CUSTOM_API_KEY` = `your-custom-key` (optional)
   - `CUSTOM_API_URL` = `your-custom-url` (optional)

4. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your API will be live at `https://your-project.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   # First deployment (follow prompts)
   vercel
   
   # Or deploy to production directly
   vercel --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add FLASK_ENV production
   vercel env add ENABLE_MOCK_MODE true
   # Add other variables as needed
   ```

## Project Structure for Vercel

```
VIrtual Shield copy/
├── api/
│   └── index.py              # Vercel entry point (exports Flask app)
├── api_server_v2.py          # Main Flask application
├── config.py                 # Configuration
├── services/                 # Service modules
├── backend/                  # Backend utilities
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
├── pyproject.toml           # Python project metadata
└── .vercelignore            # Files to exclude from deployment
```

## Configuration Files

### `vercel.json`
Configures how Vercel builds and routes your application:
- Routes all requests to the Flask app
- Sets environment variables
- Specifies the build configuration

### `pyproject.toml`
Tells Vercel where to find your Flask app:
```toml
[project.scripts]
app = "api.index:app"
```

### `api/index.py`
Entry point that exports the Flask app for Vercel's serverless functions.

## Important Notes

### Size Limitations
- **Max deployment size**: 250MB
- The `.vercelignore` file excludes:
  - Training data (`data/`)
  - Model files (`models/`)
  - Upload directory (`uploads/`)
  - Development files

### Text Detection
⚠️ **The text detection feature requires trained model files.** 

Options:
1. **Use mock mode only** (no text detection, image detection mocked)
2. **Deploy models separately** and load them from cloud storage
3. **Use smaller models** that fit within the 250MB limit

### API Keys
- Never commit API keys to your repository
- Always use Vercel's environment variables
- Set `ENABLE_MOCK_MODE=true` for testing without real API keys

## Testing Your Deployment

After deployment, test the endpoints:

```bash
# Replace YOUR_DOMAIN with your Vercel deployment URL
export API_URL="https://your-project.vercel.app"

# Health check
curl $API_URL/health

# API info
curl $API_URL/api/info

# Test root endpoint
curl $API_URL/
```

## Local Development with Vercel

Test your Vercel configuration locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Vercel CLI
vercel dev

# Or use the regular Flask server
python api_server_v2.py
```

## Troubleshooting

### Build Fails - Package Too Large
- Check `.vercelignore` is excluding unnecessary files
- Remove unused dependencies from `requirements.txt`
- Consider deploying models separately

### Environment Variables Not Working
- Ensure variables are set in Vercel dashboard
- Redeploy after changing environment variables
- Check variable names match exactly

### Import Errors
- Make sure all imports in `api/index.py` are correct
- Verify `api_server_v2.py` is not in `.vercelignore`
- Check that all required service modules are included

### 500 Internal Server Error
- Check Vercel function logs in the dashboard
- Verify all environment variables are set
- Ensure dependencies are installed correctly

## Monitoring

- View logs: Vercel Dashboard → Your Project → Deployments → Logs
- Monitor usage: Vercel Dashboard → Your Project → Analytics
- Check errors: Vercel Dashboard → Your Project → Runtime Logs

## Custom Domain

To use a custom domain:
1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Scaling

- Vercel automatically scales based on traffic
- Free tier includes:
  - 100 GB bandwidth/month
  - 100 hours serverless function execution
  - Automatic SSL
  
For higher limits, upgrade to Pro or Enterprise.

## Next Steps

1. ✅ Configure environment variables
2. ✅ Test all endpoints
3. ✅ Set up custom domain (optional)
4. ✅ Configure monitoring and alerts
5. ✅ Set up CI/CD with GitHub integration

## Resources

- [Vercel Flask Documentation](https://vercel.com/docs/frameworks/backend/flask)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Vercel Limits](https://vercel.com/docs/functions/limitations)
