#!/usr/bin/env python3
"""
Training Script for AI Text Detection Model
Uses textdescriptives features and CNN architecture
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import spacy
import textdescriptives as td
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, BatchNormalization, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import joblib
import json
from pathlib import Path
from tqdm import tqdm
import logging

# Configure TensorFlow to prevent hanging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def setup_directories():
    """Create necessary directories"""
    Path("models").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    print("✅ Directories created/verified")
    sys.stdout.flush()


def download_and_prepare_data(quick_test=False):
    """Download and prepare the dataset"""
    print("\n" + "="*70)
    print("STEP 1: Downloading and Preparing Dataset")
    if quick_test:
        print("[QUICK TEST MODE - Using subset of data]")
    print("="*70)
    
    # Clone the dataset repository
    if not os.path.exists("data/human-v-ai"):
        print("Cloning dataset repository...")
        os.system("git clone https://github.com/rsickle1/human-v-ai.git data/human-v-ai")
    else:
        print("Dataset directory already exists")
    
    # Load the CSV file
    csv_path = "data/human-v-ai/5000human_5000machine.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded dataset: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check actual label values
    print(f"Unique labels in dataset: {df['label'].unique()}")
    
    # Map labels to binary (1 = AI, 0 = Human)
    # Handle various possible label formats
    label_map = {
        "machine": 1, "Machine": 1, "MACHINE": 1, "ai": 1, "AI": 1,
        "human": 0, "Human": 0, "HUMAN": 0
    }
    
    df = df[['label', 'text']].copy()
    df["label"] = df["label"].map(label_map)
    
    # Check if mapping was successful
    if df["label"].isna().any():
        print(f"⚠️  Warning: Some labels couldn't be mapped. Unique values: {df['label'].unique()}")
        # Try to infer from the data
        unique_labels = df['label'].dropna().unique()
        if len(unique_labels) == 0:
            # No successful mapping, use original values
            print("Using original label values...")
            df = pd.read_csv(csv_path)[['label', 'text']].copy()
            unique_vals = df['label'].unique()
            if len(unique_vals) == 2:
                # Create binary mapping from whatever values exist
                df["label"] = (df["label"] == unique_vals[0]).astype(int)
                print(f"Mapped {unique_vals[0]} → 1, {unique_vals[1]} → 0")
    
    # Drop any remaining NaN labels
    df = df.dropna(subset=['label'])
    
    # If quick test mode, use only a subset
    if quick_test:
        print("\n🚀 Quick test mode: Using 1000 samples (500 per class)")
        # Sample 500 from each class
        df_ai = df[df['label'] == 1].sample(n=min(500, len(df[df['label'] == 1])), random_state=42)
        df_human = df[df['label'] == 0].sample(n=min(500, len(df[df['label'] == 0])), random_state=42)
        df = pd.concat([df_ai, df_human]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Label distribution:\n{df['label'].value_counts()}")
    print(f"Final dataset shape: {df.shape}")
    
    return df


def extract_features(df):
    """Extract textdescriptives features from text"""
    print("\n" + "="*70)
    print("STEP 2: Extracting Linguistic Features")
    print("="*70)
    
    # Load spaCy model with textdescriptives
    print("Loading spaCy model...")
    sys.stdout.flush()
    try:
        nlp = spacy.load("en_core_web_sm")
        nlp.add_pipe("textdescriptives/all")
        print("✅ spaCy model loaded successfully")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Error loading spaCy model: {e}")
        sys.stdout.flush()
        raise
    
    # Extract features with progress bar
    print("Processing texts (this may take several minutes)...")
    sys.stdout.flush()
    texts = df["text"].astype(str).tolist()
    print(f"Starting to process {len(texts)} texts...")
    sys.stdout.flush()
    
    docs = []
    try:
        for doc in tqdm(
            nlp.pipe(texts, batch_size=50, n_process=1),
            total=len(texts),
            desc="Processing texts",
            unit="text"
        ):
            docs.append(doc)
    except Exception as e:
        print(f"\n❌ Error during text processing: {e}")
        sys.stdout.flush()
        raise
    
    print("\nExtracting features from processed documents...")
    sys.stdout.flush()
    try:
        df_features = td.extract_df(docs)
        print(f"✅ Features extracted: {df_features.shape}")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Error extracting features: {e}")
        sys.stdout.flush()
        raise
    
    # Store labels separately to ensure they're preserved
    labels = df["label"].reset_index(drop=True).copy()
    
    # Handle missing values in features - drop columns with >50% missing
    print(f"Features shape before handling missing values: {df_features.shape}")
    threshold = 0.5
    df_features = df_features.dropna(thresh=int(threshold * len(df_features)), axis=1)
    print(f"Features shape after handling missing values: {df_features.shape}")
    
    # Combine cleaned features with labels
    df_final = pd.concat([df_features, labels], axis=1)
    
    # Verify label column exists
    if "label" not in df_final.columns:
        raise ValueError("Label column was lost during processing!")
    
    print(f"✅ Final dataset shape: {df_final.shape}")
    print(f"✅ Label column preserved: {df_final['label'].value_counts().to_dict()}")
    
    return df_final


def prepare_training_data(df_final):
    """Split and scale data for training"""
    print("\n" + "="*70)
    print("STEP 3: Preparing Training Data")
    print("="*70)
    
    # Verify label column exists
    if "label" not in df_final.columns:
        print(f"❌ Error: Label column not found!")
        print(f"Available columns: {df_final.columns.tolist()}")
        raise KeyError("Label column is missing from the dataset")
    
    # Separate features and labels
    X = df_final.drop(columns=["label", "text"], errors='ignore')
    y = df_final["label"]
    
    # Save feature column names for later use
    feature_columns = X.columns.tolist()
    
    # Split data: 80% train, 10% val, 10% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Reshape for Conv1D (samples, features, channels) and ensure float32
    X_train_scaled = X_train_scaled[..., np.newaxis].astype(np.float32)
    X_val_scaled = X_val_scaled[..., np.newaxis].astype(np.float32)
    X_test_scaled = X_test_scaled[..., np.newaxis].astype(np.float32)
    
    # Remove any NaN values and ensure proper data types
    mask_train = ~np.isnan(X_train_scaled).any(axis=(1, 2))
    X_train_scaled = X_train_scaled[mask_train]
    y_train = y_train.iloc[mask_train].reset_index(drop=True).values.astype(np.float32)
    
    mask_val = ~np.isnan(X_val_scaled).any(axis=(1, 2))
    X_val_scaled = X_val_scaled[mask_val]
    y_val = y_val.iloc[mask_val].reset_index(drop=True).values.astype(np.float32)
    
    mask_test = ~np.isnan(X_test_scaled).any(axis=(1, 2))
    X_test_scaled = X_test_scaled[mask_test]
    y_test = y_test.iloc[mask_test].reset_index(drop=True).values.astype(np.float32)
    
    print(f"✅ Training samples: {X_train_scaled.shape[0]}")
    print(f"✅ Validation samples: {X_val_scaled.shape[0]}")
    print(f"✅ Testing samples: {X_test_scaled.shape[0]}")
    print(f"✅ Number of features: {X_train_scaled.shape[1]}")
    
    return (X_train_scaled, X_val_scaled, X_test_scaled, 
            y_train, y_val, y_test, scaler, feature_columns)


def build_model(input_shape):
    """Build CNN model architecture"""
    model = Sequential([
        Conv1D(128, kernel_size=3, activation="relu", input_shape=input_shape),
        BatchNormalization(),
        Flatten(),
        Dense(256, activation="relu"),
        Dropout(0.4),
        Dense(128, activation="relu"),
        Dropout(0.3),
        Dense(64, activation="relu"),
        Dropout(0.2),
        Dense(1, activation="sigmoid")
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    
    return model


class ProgressCallback(tf.keras.callbacks.Callback):
    """Custom callback to show training progress immediately"""
    def on_train_begin(self, logs=None):
        print(">>> Training started, processing batches...")
        sys.stdout.flush()
        self.batch_count = 0
    
    def on_epoch_begin(self, epoch, logs=None):
        print(f"\n>>> Starting Epoch {epoch + 1}/{self.params['epochs']}")
        sys.stdout.flush()
        self.batch_count = 0
    
    def on_epoch_end(self, epoch, logs=None):
        print(f"\n>>> Epoch {epoch + 1} completed - loss: {logs['loss']:.4f}, acc: {logs['accuracy']:.4f}, val_loss: {logs['val_loss']:.4f}, val_acc: {logs['val_accuracy']:.4f}")
        sys.stdout.flush()
    
    def on_batch_end(self, batch, logs=None):
        self.batch_count += 1
        if self.batch_count % 2 == 0:  # Print every 2 batches
            print(".", end="")
            sys.stdout.flush()


def train_model(model, X_train, y_train, X_val, y_val, quick_test=False):
    """Train the model"""
    print("\n" + "="*70)
    print("STEP 4: Training Model")
    if quick_test:
        print("[QUICK TEST MODE - Reduced epochs and batch size]")
    print("="*70)
    
    # Callbacks
    patience = 3 if quick_test else 10
    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=patience,
        restore_best_weights=True
    )
    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2 if quick_test else 3
    )
    progress_callback = ProgressCallback()
    
    # Training parameters
    epochs = 5 if quick_test else 150
    batch_size = 64 if quick_test else 32
    
    print(f"Training with {epochs} max epochs, batch size {batch_size}")
    print(f"X_train shape: {X_train.shape}, dtype: {X_train.dtype}")
    print(f"y_train shape: {y_train.shape}, dtype: {y_train.dtype}")
    print(f"X_val shape: {X_val.shape}, dtype: {X_val.dtype}")
    print(f"y_val shape: {y_val.shape}, dtype: {y_val.dtype}")
    
    # Validate data for any issues
    print("\nValidating data...")
    print(f"X_train - has NaN: {np.isnan(X_train).any()}, has Inf: {np.isinf(X_train).any()}")
    print(f"y_train - has NaN: {np.isnan(y_train).any()}, has Inf: {np.isinf(y_train).any()}")
    print(f"X_train range: [{X_train.min():.4f}, {X_train.max():.4f}]")
    print(f"y_train unique values: {np.unique(y_train)}")
    print(f"y_train distribution: 0={np.sum(y_train==0)}, 1={np.sum(y_train==1)}")
    sys.stdout.flush()
    
    print("\n🚀 Starting training...")
    sys.stdout.flush()
    
    # Train
    try:
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr, progress_callback],
            verbose=1  # Use verbose=1 to ensure training progress is shown
        )
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        raise
    
    print("✅ Training complete!")
    
    return history


def evaluate_model(model, X_test, y_test):
    """Evaluate model on test set"""
    print("\n" + "="*70)
    print("STEP 5: Evaluating Model")
    print("="*70)
    
    # Predictions
    y_pred_proba = model.predict(X_test, verbose=1)
    y_pred = (y_pred_proba > 0.5).astype(int).flatten()
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    # Print results
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC AUC:   {roc_auc:.4f}")
    print("\nConfusion Matrix:")
    print(conf_matrix)
    
    metrics = {
        'accuracy': float(acc),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc)
    }
    
    return metrics


def save_artifacts(model, scaler, feature_columns, metrics):
    """Save model and preprocessing artifacts"""
    print("\n" + "="*70)
    print("STEP 6: Saving Model and Artifacts")
    print("="*70)
    
    # Save model
    model_path = "models/ai_text_detector.h5"
    model.save(model_path)
    print(f"✅ Model saved: {model_path}")
    
    # Save scaler
    scaler_path = "models/scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved: {scaler_path}")
    
    # Save feature columns
    columns_path = "models/feature_columns.json"
    with open(columns_path, 'w') as f:
        json.dump(feature_columns, f)
    print(f"✅ Feature columns saved: {columns_path}")
    
    # Save metrics
    metrics_path = "models/metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Metrics saved: {metrics_path}")
    
    # Print file sizes
    model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"\nModel size: {model_size_mb:.2f} MB")


def main():
    """Main training pipeline"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train AI Text Detection Model')
    parser.add_argument(
        '--quick-test',
        action='store_true',
        help='Quick test mode: Use subset of data and fewer epochs (~10 min training)'
    )
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("AI TEXT DETECTION MODEL - TRAINING PIPELINE")
    if args.quick_test:
        print("🚀 QUICK TEST MODE - Reduced dataset and epochs")
        print("   Expected time: ~10 minutes")
        print("   Note: Lower accuracy, for testing only")
    print("="*70)
    
    try:
        # Setup
        setup_directories()
        
        # Load data
        df = download_and_prepare_data(quick_test=args.quick_test)
        
        # Extract features
        df_final = extract_features(df)
        
        # Prepare training data
        (X_train, X_val, X_test, y_train, y_val, y_test,
         scaler, feature_columns) = prepare_training_data(df_final)
        
        # Build model
        input_shape = (X_train.shape[1], 1)
        model = build_model(input_shape)
        model.summary()
        
        # Train model
        history = train_model(model, X_train, y_train, X_val, y_val, quick_test=args.quick_test)
        
        # Evaluate model
        metrics = evaluate_model(model, X_test, y_test)
        
        # Save everything
        save_artifacts(model, scaler, feature_columns, metrics)
        
        print("\n" + "="*70)
        if args.quick_test:
            print("✅ QUICK TEST COMPLETE - Model saved (testing only!)")
        else:
            print("✅ TRAINING COMPLETE - Model ready for deployment!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
