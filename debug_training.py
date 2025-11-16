#!/usr/bin/env python3
"""
Debug script to test TensorFlow training
"""
import os
import sys
import numpy as np
import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("GPU available:", tf.config.list_physical_devices('GPU'))

# Configure TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

# Create simple dummy data
print("\nCreating dummy data...")
X_train = np.random.randn(756, 68, 1).astype(np.float32)
y_train = np.random.randint(0, 2, 756).astype(np.float32)
X_val = np.random.randn(91, 68, 1).astype(np.float32)
y_val = np.random.randint(0, 2, 91).astype(np.float32)

print(f"X_train shape: {X_train.shape}, dtype: {X_train.dtype}")
print(f"y_train shape: {y_train.shape}, dtype: {y_train.dtype}")

# Build simple model
print("\nBuilding model...")
model = tf.keras.Sequential([
    tf.keras.layers.Conv1D(128, kernel_size=3, activation="relu", input_shape=(68, 1)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

print("\nModel compiled. Starting training...")
sys.stdout.flush()

# Custom callback
class DebugCallback(tf.keras.callbacks.Callback):
    def on_train_begin(self, logs=None):
        print(">>> on_train_begin called")
        sys.stdout.flush()
    
    def on_epoch_begin(self, epoch, logs=None):
        print(f">>> on_epoch_begin: epoch {epoch}")
        sys.stdout.flush()
    
    def on_batch_begin(self, batch, logs=None):
        if batch == 0:
            print(f">>> on_batch_begin: batch {batch}")
            sys.stdout.flush()
    
    def on_batch_end(self, batch, logs=None):
        if batch % 2 == 0:
            print(f">>> on_batch_end: batch {batch}, loss={logs.get('loss', 'N/A')}")
            sys.stdout.flush()
    
    def on_epoch_end(self, epoch, logs=None):
        print(f">>> on_epoch_end: epoch {epoch}, loss={logs['loss']:.4f}")
        sys.stdout.flush()
    
    def on_train_end(self, logs=None):
        print(">>> on_train_end called")
        sys.stdout.flush()

# Train with verbose output
try:
    print("Calling model.fit()...")
    sys.stdout.flush()
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=2,
        batch_size=64,
        callbacks=[DebugCallback()],
        verbose=1  # Try with verbose=1 first
    )
    
    print("\n✅ Training completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
