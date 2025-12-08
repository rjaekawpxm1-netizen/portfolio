import sys
import os
import librosa
import numpy as np
from tensorflow.keras.models import load_model

# 모델 로드
model = load_model("C:/Users/Huni/Desktop/Cap/UnifiedBackend/scripts/emotion_model_5class.h5")

# 실제 감정은 4개
emotion_labels = ["Anger", "Anxiety", "Sadness", "Normal"]

def extract_features(path):
    # 3초 기준으로 맞추기
    target_sr = 22050
    target_duration = 3  # seconds
    y, sr = librosa.load(path, sr=target_sr, duration=target_duration)

    # 만약 소리가 3초보다 짧으면 뒤를 0으로 채워서 항상 같은 길이 되게
    expected_len = target_sr * target_duration  # 22050 * 3 = 66150
    if len(y) < expected_len:
        pad_width = expected_len - len(y)
        y = np.pad(y, (0, pad_width), mode="constant")

    mfcc = librosa.feature.mfcc(y=y, sr=target_sr, n_mfcc=40)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    mfcc_mean = np.expand_dims(mfcc_mean, axis=0)
    return mfcc_mean

def analyze_audio(audio_path):
    if not os.path.exists(audio_path):
        print("오디오 파일을 찾을 수 없습니다:", audio_path)
        return 0.0

    features = extract_features(audio_path)
    pred = model.predict(features, verbose=0)[0]

    # pred 길이와 라벨 길이 확인
    if len(pred) != len(emotion_labels):
        print("라벨 개수와 모델 출력 개수가 다릅니다.")
        print("model output length:", len(pred))
        print("labels length:", len(emotion_labels))
        # 여기서는 그냥 가장 큰 값만 점수로 리턴
        top_prob = float(np.max(pred))
        print(f"{top_prob * 100:.2f}")
        return top_prob * 100

    # 감정 확률 매핑
    emotion_probs = {emotion_labels[i]: float(pred[i]) for i in range(len(emotion_labels))}
    top_emotion = max(emotion_probs, key=emotion_probs.get)
    top_prob = emotion_probs[top_emotion]

    # 디버깅용 출력
    print("emotion probs:", emotion_probs)
    print("top emotion:", top_emotion, top_prob)

    # 점수 계산 (4개 버전)
    if top_emotion == 'Normal':
        score = top_prob * 25
    elif top_emotion == 'Anger':
        score = 25 + top_prob * 25
    elif top_emotion == 'Anxiety':
        score = 50 + top_prob * 25
    elif top_emotion == 'Sadness':
        score = 75 + top_prob * 25
    else:
        score = 0

    # 최종 출력은 숫자만
    print(f"{score:.2f}")
    return score

if __name__ == "__main__":
    audio_path = sys.argv[1].replace("\\", "/")
    analyze_audio(audio_path)
