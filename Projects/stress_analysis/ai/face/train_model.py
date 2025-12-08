import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import Callback, ModelCheckpoint, EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import time

# ==========================================
# 설정
# ==========================================
BASE_PATH = r"C:\Users\hans6\dataset\한국인 감정인식을 위한 복합 영상\Processed"
CSV_PATH = os.path.join(BASE_PATH, "dataset_fixed.csv")
CHECKPOINT_DIR = os.path.join(BASE_PATH, "checkpoints_monitor")
BEST_MODEL_PATH = os.path.join(BASE_PATH, "emotion_model_best_monitor.keras")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# ==========================================
# 데이터 로드
# ==========================================
df = pd.read_csv(CSV_PATH)
emotion_labels = sorted(df["label"].unique())
df["label_idx"] = df["label"].astype("category").cat.codes

train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["label_idx"], random_state=42)

# ==========================================
# RGB 변환 함수
# ==========================================
def gray_to_rgb(img):
    if img.shape[-1] == 1:
        img = tf.image.grayscale_to_rgb(img)
    return img

# ==========================================
# 데이터 제너레이터
# ==========================================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    preprocessing_function=gray_to_rgb,
    rotation_range=25,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True
)
val_datagen = ImageDataGenerator(rescale=1./255, preprocessing_function=gray_to_rgb)

train_gen = train_datagen.flow_from_dataframe(
    train_df, x_col="path", y_col="label", target_size=(160,160),
    class_mode="categorical", batch_size=32, shuffle=True
)
val_gen = val_datagen.flow_from_dataframe(
    val_df, x_col="path", y_col="label", target_size=(160,160),
    class_mode="categorical", batch_size=32, shuffle=False
)

# ==========================================
# Class Weight 계산
# ==========================================
class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(train_df["label_idx"]),
    y=train_df["label_idx"]
)
class_weights = dict(enumerate(class_weights))

# ==========================================
# 모델 구성
# ==========================================
base_model = EfficientNetB2(include_top=False, weights=None, input_tensor=Input(shape=(160,160,3)))
x = GlobalAveragePooling2D()(base_model.output)
x = Dropout(0.5)(x)
output = Dense(len(emotion_labels), activation="softmax")(x)
model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ==========================================
# 실시간 모니터링 콜백
# ==========================================
class LiveProgress(Callback):
    def on_train_begin(self, logs=None):
        self.start_time = time.time()
        print("\n🚀 학습 시작\n")

    def on_epoch_end(self, epoch, logs=None):
        elapsed = time.time() - self.start_time
        acc = logs.get('accuracy', 0)
        val_acc = logs.get('val_accuracy', 0)
        loss = logs.get('loss', 0)
        val_loss = logs.get('val_loss', 0)
        percent = (epoch + 1) / self.params['epochs'] * 100
        eta = (elapsed / (epoch + 1)) * (self.params['epochs'] - (epoch + 1))
        bar = "█" * int(percent / 4) + "-" * (25 - int(percent / 4))
        print(f"\rEpoch [{epoch+1}/{self.params['epochs']}] |{bar}| "
              f"Acc: {acc:.3f}  Val_Acc: {val_acc:.3f}  "
              f"Loss: {loss:.3f}  Val_Loss: {val_loss:.3f}  ETA: {eta/60:.1f} min", end='')

    def on_train_end(self, logs=None):
        print("\n✅ 학습 완료!\n")

# ==========================================
# 콜백 설정
# ==========================================
callbacks = [
    LiveProgress(),
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True, verbose=1),
    ModelCheckpoint(filepath=BEST_MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1)
]

# ==========================================
# 학습 시작
# ==========================================
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=50,
    callbacks=callbacks,
    class_weight=class_weights
)

print(f"\n📁 Best 모델 저장 위치: {BEST_MODEL_PATH}")
