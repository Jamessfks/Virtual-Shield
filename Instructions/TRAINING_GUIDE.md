# Training Guide - Quick Reference

## 🆕 New Features Added

### 1. Real-time Progress Bars
The training script now shows progress bars using `tqdm` for:
- Text processing (feature extraction)
- Model training (shown by TensorFlow/Keras)

### 2. Quick Test Mode
A new `--quick-test` flag for rapid testing (~10 minutes total)

---

## Usage

### Full Training (Production Model)
**Time**: 25-40 minutes  
**Accuracy**: ~92%

```bash
python3 train_text_detector.py
```

### Quick Test Mode (Testing Only)
**Time**: ~8-12 minutes  
**Accuracy**: ~75-85% (lower, for testing only)

```bash
python3 train_text_detector.py --quick-test
```

---

## What Quick Test Mode Does

### Data Reduction
- Uses **1,000 samples** instead of 10,000
- 500 AI-generated + 500 human-written
- **~80% faster** feature extraction

### Training Optimization
- **20 epochs** max (instead of 150)
- **Batch size 64** (instead of 32)
- **Early stopping patience: 3** (instead of 10)
- **~70% faster** training

### Expected Timeline (Quick Test)
1. ✅ Dataset download: 0 min (already downloaded)
2. 🔄 Feature extraction: 2-4 minutes (1,000 texts vs 10,000)
3. 🔄 Model training: 3-5 minutes (20 epochs vs 150)
4. ✅ Evaluation & saving: 1 minute

**Total: ~8-12 minutes**

---

## Progress Bar Output Example

### Text Processing
```
Processing texts: 100%|████████████| 1000/1000 [02:34<00:00,  6.48text/s]
```

### Model Training
```
Epoch 1/20
25/25 [==============================] - 5s 195ms/step - loss: 0.6234 - accuracy: 0.6450 - val_loss: 0.5123 - val_accuracy: 0.7500
```

---

## When to Use Each Mode

### Use Full Training When:
✅ Preparing for production deployment  
✅ Need highest accuracy  
✅ Have time (25-40 minutes)  
✅ Final model for users  

### Use Quick Test When:
✅ Testing if the pipeline works  
✅ Debugging code changes  
✅ Verifying dependencies installed  
✅ Quick smoke test (~10 min)  

---

## Installation

If you haven't installed `tqdm` yet:

```bash
pip install tqdm==4.66.1

# Or install all dependencies
pip install -r requirements.txt
```

---

## Examples

### Check if everything works (Quick)
```bash
# First time - test the pipeline
python3 train_text_detector.py --quick-test

# Output shows progress bars and completes in ~10 min
```

### Train production model
```bash
# When ready for real model
python3 train_text_detector.py

# Takes 25-40 minutes but achieves ~92% accuracy
```

### Help
```bash
python3 train_text_detector.py --help
```

---

## Comparing Models

| Mode | Time | Samples | Epochs | Accuracy | Use Case |
|------|------|---------|--------|----------|----------|
| **Full** | 25-40 min | 10,000 | Up to 150 | ~92% | Production |
| **Quick Test** | 8-12 min | 1,000 | Up to 20 | ~75-85% | Testing |

---

## Notes

⚠️ **Quick test models** are saved to the same location as full models. If you need to keep both:
1. Train quick test first
2. Rename or move the `models/` folder
3. Train full model

💡 **Tip**: Quick test is perfect for:
- Verifying your setup works
- Testing code changes
- CI/CD pipelines
- Development iterations

🚀 **For production**: Always use full training without the `--quick-test` flag.

---

## Monitoring Progress

While training, you can monitor in another terminal:

```bash
# Watch for model files
while true; do clear; ls -lh models/ 2>/dev/null || echo "Training..."; sleep 5; done

# Check process
ps aux | grep train_text_detector | grep -v grep
```

---

## Next Steps After Training

1. Verify model files exist:
   ```bash
   ls -lh models/
   # Should show: ai_text_detector.h5, scaler.pkl, feature_columns.json, metrics.json
   ```

2. Start the API server:
   ```bash
   python3 api_server_v2.py
   ```

3. Test the endpoint:
   ```bash
   curl http://localhost:5001/api/info
   ```

4. Open test interface:
   ```bash
   open test_text_detection.html
   ```
