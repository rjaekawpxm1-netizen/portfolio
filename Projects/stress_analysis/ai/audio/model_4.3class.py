import os
import numpy as np
import pandas as pd
import librosa
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, BatchNormalization, Dense, Dropout, Flatten
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# ===== 설정 =====
DATASET_ROOT = "C:/Users/hans6/audio_ai/raw_dataset/"
DATASET_FOLDERS = ["data_5", "data_5.2","sorted_wav_files"]
MODEL_NAME = "emotion_model_5class.h5"
VALID_EMOTIONS = ['angry', 'anxious', 'neutral', 'sad']

# ===== 라벨 매핑 함수 =====
def map_emotion(label):
    label = label.lower().replace("2", "").strip()
    if "anger" in label or "angry" in label or "angry2" in label:
        return "angry"
    elif "anxious" in label or "fear2" in label or "fear" in label:
        return "anxious"
    elif "neutral" in label or "neutral2" in label:
        return "neutral"
    elif "sad" in label or "sadness2" in label:
        return "sad"
    else:
        return None  # 제거 대상

# ===== 데이터셋 로드 =====
def load_dataset():
    file_paths, labels = [], []
    for folder in DATASET_FOLDERS:
        dataset_path = os.path.join(DATASET_ROOT, folder)
        if not os.path.exists(dataset_path):
            continue
        for emotion_folder in os.listdir(dataset_path):
            emotion_path = os.path.join(dataset_path, emotion_folder)
            if not os.path.isdir(emotion_path):
                continue
            mapped_label = map_emotion(emotion_folder)
            if mapped_label not in VALID_EMOTIONS:
                continue
            for file in os.listdir(emotion_path):
                if file.endswith(".wav"):
                    file_paths.append(os.path.join(emotion_path, file))
                    labels.append(mapped_label)
    return pd.DataFrame({'file_path': file_paths, 'emotion': labels})

print("📂 데이터셋 로드 중...")
data = load_dataset()
print(f"✅ 총 {len(data)}개의 유효한 샘플")

# ===== 특징 추출 =====
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=16000, duration=3)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y)
        rmse = librosa.feature.rms(y=y)
        features = np.vstack([mfcc, chroma, contrast, tonnetz, zcr, rmse])
        return np.mean(features.T, axis=0)
    except Exception as e:
        print(f"[오류] {file_path}: {e}")
        return None

print("🔍 특징 추출 중...")
features = []
for idx, row in data.iterrows():
    if idx % 100 == 0:
        print(f"{idx+1}/{len(data)} 처리 중...")
    feat = extract_features(row['file_path'])
    features.append(feat)

# ===== 유효 데이터 필터링 =====
valid_data = data.iloc[[i for i, f in enumerate(features) if f is not None]]
X = np.array([f for f in features if f is not None])
y = valid_data['emotion']

# ===== 전처리 =====
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

le = LabelEncoder()
y_encoded = le.fit_transform(y)
y_categorical = pd.get_dummies(y_encoded).values

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_categorical, 
    test_size=0.2, 
    stratify=y_encoded,
    random_state=42
)

# ===== 모델 구성 =====
model = Sequential([
    Conv1D(256, 5, activation='relu', input_shape=(X_train.shape[1], 1)),
    BatchNormalization(),
    MaxPooling1D(2),
    Conv1D(128, 5, activation='relu'),
    BatchNormalization(),
    MaxPooling1D(2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(len(le.classes_), activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

print("🚀 모델 학습 시작")
history = model.fit(
    X_train.reshape(-1, X_train.shape[1], 1),
    y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=[
        EarlyStopping(patience=15, restore_best_weights=True),
        ReduceLROnPlateau(factor=0.1, patience=5)
    ],
    verbose=1
)

# ===== 성능 평가 =====
test_loss, test_acc = model.evaluate(X_test.reshape(-1, X_test.shape[1], 1), y_test, verbose=0)
print(f"\n✅ 테스트 정확도: {test_acc:.4f}")

# ===== 정밀도/재현율/F1-score =====
preds = model.predict(X_test.reshape(-1, X_test.shape[1], 1))
pred_labels = np.argmax(preds, axis=1)
true_labels = np.argmax(y_test, axis=1)

print("\n📊 Classification Report:")
print(classification_report(true_labels, pred_labels, target_names=le.classes_))

cm = confusion_matrix(true_labels, pred_labels)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
disp.plot(cmap='Blues')
plt.title("Confusion Matrix")
plt.show()

# ===== 모델 및 전처리기 저장 =====
model.save(MODEL_NAME)
joblib.dump(scaler, "scaler_5class.pkl")
joblib.dump(le, "label_encoder_5class.pkl")
print("\n💾 모델과 전처리기 저장 완료!")
