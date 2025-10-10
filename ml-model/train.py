# ==========================
# train.py
# ==========================

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2 # type: ignore
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D # type: ignore
from tensorflow.keras.models import Model # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.callbacks import ModelCheckpoint # type: ignore

# ==========================
# STEP 0: GPU Setup
# ==========================
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Enable dynamic memory allocation
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("✅ GPU detected. Memory growth enabled.")
    except RuntimeError as e:
        print("⚠️ Error setting GPU memory growth:", e)
else:
    print("⚠️ No GPU detected. Training will run on CPU.")

# ==========================
# STEP 1: Dataset Setup
# ==========================
import os
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 123  # Consistent seed value for reproducibility
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Define the dataset directory
DATA_DIR = "C:/Users/dheer/OneDrive/Desktop/smartwaste360/ml-model/images"  # <-- Change this to your actual dataset path

# Validate dataset folder structure
subfolders = [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode='categorical'
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode='categorical'
)

# Save class names BEFORE mapping
class_names = train_ds.class_names
num_classes = len(class_names)
print("✅ Classes detected:", class_names)

# ==========================
# STEP 2: Data Augmentation & Normalization
# ==========================
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.2),
    tf.keras.layers.RandomZoom(0.2),
    tf.keras.layers.RandomTranslation(0.1, 0.1)
])
normalization_layer = tf.keras.layers.Rescaling(1./255)

train_ds = train_ds.map(lambda x, y: (normalization_layer(data_augmentation(x)), y),
                        num_parallel_calls=tf.data.AUTOTUNE)
val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y),
                    num_parallel_calls=tf.data.AUTOTUNE)

# Prefetch for performance
train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

# ==========================
# STEP 3: Build MobileNetV2 Model
# ==========================
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
output = Dense(num_classes, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=output)

# Freeze base model layers
for layer in base_model.layers:
    layer.trainable = False

model.compile(optimizer=Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

checkpoint = ModelCheckpoint('mobilenet_waste_classifier.h5', save_best_only=True,
                             monitor='val_accuracy', mode='max')

# ==========================
# STEP 4: Train Model
# ==========================
print("✅ Starting training...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    callbacks=[checkpoint]
)
print("✅ Training complete. Model saved as mobilenet_waste_classifier.h5")

# ==========================
# STEP 5: Convert to TFLite
# ==========================
print("✅ Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
with open("mobilenet_waste_classifier.tflite", "wb") as f:
    f.write(tflite_model)
print("✅ Model converted to TFLite format.")
