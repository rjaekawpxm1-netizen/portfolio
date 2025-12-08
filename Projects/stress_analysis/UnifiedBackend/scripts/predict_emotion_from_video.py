import sys
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
import tensorflow as tf
import os

def focal_loss_fixed(y_true, y_pred):
    gamma = 2.0
    alpha = 0.25
    epsilon = K.epsilon()
    y_pred = K.clip(y_pred, epsilon, 1. - epsilon)
    cross_entropy = -y_true * K.log(y_pred)
    loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy
    return K.sum(loss, axis=1)

# 모델 로드
model = load_model(
    "C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/fer2013_best_valacc.keras",
    custom_objects={'focal_loss_fixed': focal_loss_fixed}
)

emotion_labels = ["Anger", "Anxiety", "Sadness", "Normal"]

def preprocess_frame(frame):
    # 학습 당시 grayscale 가능성 고려 → BGR→GRAY→3채널 복제
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(gray, (160, 160))
    img = np.stack((img,) * 3, axis=-1)  # (160,160,3)
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def analyze_video(video_path):
    if not os.path.exists(video_path):
        print("0.00", flush=True)
        return 0.0

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    # 초당 5프레임씩 추출 (기존보다 다양하게)
    frame_interval = max(1, int(fps // 5))
    predictions = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            img = preprocess_frame(frame)
            pred = model.predict(img, verbose=0)[0]
            pred = tf.nn.softmax(pred).numpy()
            if not np.isnan(pred).any():
                predictions.append(pred)

        frame_count += 1

    cap.release()

    if not predictions:
        print("0.00", flush=True)
        return 0.0

    predictions = np.array(predictions)
    mean_probs = np.mean(predictions, axis=0)

    if np.isnan(mean_probs).any():
        print("0.00", flush=True)
        return 0.0

    top_emotion_idx = np.argmax(mean_probs)
    top_emotion = emotion_labels[top_emotion_idx]
    top_prob = float(mean_probs[top_emotion_idx])

    # 감정별 점수 구간
    if top_emotion == 'Normal':
        score = top_prob * 25
    elif top_emotion == 'Anger':
        score = 25 + top_prob * 25
    elif top_emotion == 'Anxiety':
        score = 50 + top_prob * 25
    elif top_emotion == 'Sadness':
        score = 75 + top_prob * 25
    else:
        score = 0.0

    if np.isnan(score):
        score = 0.0

    # 디버깅용 로그
    print(f"평균 확률: {mean_probs}")
    print(f"감정: {top_emotion} ({top_prob:.2f})")
    print(f"{score:.2f}", flush=True)

    return score

if __name__ == "__main__":
    video_path = sys.argv[1].replace("\\", "/")
    analyze_video(video_path)
