# Quick Start Guide - AI Text Detection Integration

This guide will walk you through training the model and deploying the complete AI text detection system.

## Prerequisites

- Python 3.8+ installed
- 4GB+ RAM available
- 2GB disk space for model and data
- Internet connection for downloading dataset

## Step-by-Step Setup

### Step 1: Install Dependencies (5 minutes)

```bash
# Navigate to project directory
cd "/Users/jameszhao/Desktop/VIrtual Shield copy"

# Install all required packages
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
```

**Expected output**: All packages install successfully without errors.

### Step 2: Train the Model (15-30 minutes)

```bash
# Run the training script
python train_text_detector.py
```

**What to expect:**
1. Script downloads dataset (~10MB)
2. Extracts linguistic features (10-15 minutes)
3. Trains CNN model (10-15 minutes)
4. Saves trained model to `models/` directory
5. Displays final accuracy metrics (~92%)

**Output structure:**
```
VIrtual Shield copy/
├── models/
│   ├── ai_text_detector.h5      # Trained model (~2.5 MB)
│   ├── scaler.pkl                 # Feature scaler
│   ├── feature_columns.json       # Feature names
│   └── metrics.json               # Performance metrics
└── data/
    └── human-v-ai/                # Downloaded dataset
```

### Step 3: Start the API Server

```bash
# Start the server
python3 api_server_v2.py
```

**Expected output:**
```
======================================================================
AI Screenshot Detector API Server - Production Version
======================================================================
  Environment.................... production
  Host........................... 0.0.0.0
  Port........................... 5001
  Debug.......................... False
  ...
======================================================================
✅ Text detector service ready
Server URL: http://0.0.0.0:5001
```

### Step 4: Test the System

#### Option A: Using the Test Web Interface

1. Open `test_text_detection.html` in your browser:
   ```bash
   open test_text_detection.html
   ```

2. Test with file upload or text paste
3. View classification results instantly

#### Option B: Using cURL

Test with a sample text file:
```bash
# Create a test file
echo "This is a sample text to test the AI detection system." > test.txt

# Analyze it
curl -X POST http://localhost:5001/api/analyze-text \
  -F "file=@test.txt"
```

Test with direct text:
```bash
curl -X POST http://localhost:5001/api/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Artificial intelligence has revolutionized the way we approach complex problems in modern computing."}'
```

#### Option C: Using Python

```python
import requests

# Test file upload
with open('test.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:5001/api/analyze-text',
        files={'file': f}
    )
    print(response.json())

# Test direct text
response = requests.post(
    'http://localhost:5001/api/analyze-text',
    json={'text': 'Your text here...'}
)
print(response.json())
```

### Step 5: Verify Everything Works

Check API info:
```bash
curl http://localhost:5001/api/info
```

Look for this in the response:
```json
{
  "config": {
    "text_model_ready": true,
    "text_model": "CNN with textdescriptives features"
  }
}
```

## Common Issues & Solutions

### Issue 1: Model Files Not Found

**Error**: `Text detector not ready - Model not trained`

**Solution**:
```bash
# Make sure training completed successfully
python train_text_detector.py

# Verify model files exist
ls -la models/
```

### Issue 2: spaCy Model Missing

**Error**: `Can't find model 'en_core_web_sm'`

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue 3: Import Errors

**Error**: `ModuleNotFoundError: No module named 'tensorflow'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 4: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Kill existing process
lsof -ti:5001 | xargs kill -9

# Or use a different port
# Edit api_server_v2.py and change FLASK_PORT in config
```

### Issue 5: Out of Memory During Training

**Error**: Process killed or memory error

**Solution**:
Edit `train_text_detector.py`, line 197:
```python
batch_size=16,  # Reduce from 32
```

## Testing with Sample Texts

### Human-Written Sample
Create `human_sample.txt`:
```
The integration of artificial intelligence into modern healthcare systems has sparked 
both excitement and concern among medical professionals. While AI algorithms demonstrate 
remarkable accuracy in diagnostic imaging, questions remain about liability and the 
preservation of the doctor-patient relationship.
```

### AI-Generated Sample
Create `ai_sample.txt`:
```
Artificial intelligence represents a transformative technology that is revolutionizing 
multiple industries. Its applications span from healthcare diagnostics to autonomous 
vehicles, demonstrating unprecedented capabilities in pattern recognition and 
decision-making processes.
```

Test both:
```bash
curl -X POST http://localhost:5001/api/analyze-text -F "file=@human_sample.txt"
curl -X POST http://localhost:5001/api/analyze-text -F "file=@ai_sample.txt"
```

## Understanding the Results

### Classification Output

```json
{
  "classification": "AI-Generated",
  "ai_probability": 0.8542,
  "human_probability": 0.1458,
  "confidence": "high",
  "confidence_score": 0.8542
}
```

**Interpretation:**
- **classification**: Final verdict (AI-Generated or Human-Written)
- **ai_probability**: 0.0-1.0 scale (higher = more likely AI)
- **confidence**: high (>90%), medium (70-90%), low (<70%)
- **confidence_score**: Most confident probability

### Confidence Levels

| Level | Threshold | Meaning |
|-------|-----------|---------|
| **High** | >90% | Very reliable, act on result |
| **Medium** | 70-90% | Generally reliable, verify if critical |
| **Low** | <70% | Uncertain, manual review needed |

## Performance Expectations

### Processing Time
- Text extraction: 0.1-1.0 seconds
- Feature extraction: 1-3 seconds
- Model inference: 0.1-0.5 seconds
- **Total**: 1-5 seconds per request

### Accuracy
- Overall: ~92%
- Long texts (>500 words): ~95%
- Short texts (<50 words): ~75%

### Best Results With
✅ Essays (500-2000 words)
✅ Articles and blog posts
✅ Academic writing
✅ Technical documentation

### Lower Accuracy With
⚠️ Very short texts (<50 words)
⚠️ Poetry and creative writing
⚠️ Highly technical jargon
⚠️ Non-English text

## Integration Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] spaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] Model trained (`python train_text_detector.py`)
- [ ] Model files exist in `models/` directory
- [ ] API server starts without errors
- [ ] `/api/info` shows `text_model_ready: true`
- [ ] Test file upload works
- [ ] Test direct text input works
- [ ] Results display correctly

## Next Steps

### 1. Frontend Integration

Add text detection to your existing web UI. See `test_text_detection.html` for reference implementation.

### 2. Production Deployment

Consider:
- Adding authentication/API keys
- Rate limiting per user
- Caching results for identical texts
- Load balancing for high traffic
- Monitoring and logging

### 3. Model Monitoring

Track:
- Prediction distribution (AI vs Human ratio)
- Average confidence scores
- Processing times
- Error rates

### 4. Continuous Improvement

- Collect edge cases (low confidence predictions)
- Gather user feedback
- Retrain periodically with new data
- A/B test model improvements

## Directory Structure

```
VIrtual Shield copy/
├── train_text_detector.py          # Training script
├── api_server_v2.py                 # API server with text detection
├── test_text_detection.html         # Test web interface
├── TEXT_DETECTION_README.md         # Detailed documentation
├── requirements.txt                 # All dependencies
│
├── models/                          # Trained model artifacts
│   ├── ai_text_detector.h5
│   ├── scaler.pkl
│   ├── feature_columns.json
│   └── metrics.json
│
├── services/                        # Service modules
│   ├── text_detector.py            # Text detection service
│   ├── text_extractor.py           # File text extraction
│   └── detector.py                 # Image detection
│
└── data/                           # Training data
    └── human-v-ai/                 # Dataset
```

## Support & Documentation

- **Quick Start**: This file (QUICKSTART.md)
- **Detailed Docs**: TEXT_DETECTION_README.md
- **API Guide**: API_INTEGRATION_GUIDE.md
- **Main README**: README.md

## Command Reference

```bash
# Training
python train_text_detector.py

# Start server
python api_server_v2.py

# Test API
curl http://localhost:5001/api/info
curl -X POST http://localhost:5001/api/analyze-text -F "file=@test.txt"
curl -X POST http://localhost:5001/api/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text..."}'

# View logs
tail -f logs/app.log  # If logging to file

# Kill server
lsof -ti:5001 | xargs kill -9
```

## Success Criteria

You've successfully set up the system when:

1. ✅ `python train_text_detector.py` completes without errors
2. ✅ `models/` directory contains 4 files
3. ✅ `python api_server_v2.py` starts and shows "Text detector service ready"
4. ✅ `/api/info` endpoint returns `text_model_ready: true`
5. ✅ Test file upload returns valid classification results
6. ✅ Test direct text returns valid classification results

## Troubleshooting Contact

If you encounter issues not covered here:
1. Check TEXT_DETECTION_README.md for detailed troubleshooting
2. Review error logs in terminal output
3. Verify all dependencies are installed correctly
4. Ensure model training completed successfully

---

**Congratulations!** Your AI text detection system is now ready to use. 🎉
