import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report

# 경로
BASE_PATH = r"C:\Users\hans6\dataset\한국인 감정인식을 위한 복합 영상\Processed"
CSV_PATH = os.path.join(BASE_PATH, "dataset_fixed.csv")
MODEL_PATH = os.path.join(BASE_PATH, "emotion_model_best_monitor.keras")

df = pd.read_csv(CSV_PATH)
emotion_labels = sorted(df["label"].unique())

from sklearn.model_selection import train_test_split
_, val_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)

def gray_to_rgb(img):
    if img.shape[-1] == 1:
        img = tf.image.grayscale_to_rgb(img)
    return img

val_datagen = ImageDataGenerator(rescale=1./255, preprocessing_function=gray_to_rgb)
val_gen = val_datagen.flow_from_dataframe(
    val_df, x_col="path", y_col="label", target_size=(160,160),
    class_mode="categorical", batch_size=32, shuffle=False
)

model = load_model(MODEL_PATH, compile=False)
print(f"\n✅ 모델 로드 완료: {MODEL_PATH}")

pred_probs = model.predict(val_gen, verbose=1)
pred_classes = np.argmax(pred_probs, axis=1)
true_classes = val_gen.classes
class_labels = list(val_gen.class_indices.keys())

report = classification_report(true_classes, pred_classes, target_names=class_labels, digits=4, output_dict=True)

# 표 형태 출력
lines = []
lines.append("\n📊 감정별 성능 평가 결과\n")
lines.append(f"{'Emotion':<10} {'Precision':>10} {'Recall':>10} {'F1-score':>10} {'Support':>10}")
lines.append("-"*55)
for label in class_labels:
    r = report[label]
    lines.append(f"{label:<10} {r['precision']:>10.2f} {r['recall']:>10.2f} {r['f1-score']:>10.2f} {int(r['support']):>10}")
lines.append("-"*55)
lines.append(f"{'Accuracy':<10} {report['accuracy']*100:>10.2f}%")

# 터미널에 출력
output = "\n".join(lines)
print(output)

# 파일로 저장
save_path = os.path.join(BASE_PATH, "evaluation_result.txt")
with open(save_path, "w", encoding="utf-8") as f:
    f.write(output)
print(f"\n✅ 평가 결과 저장 완료: {save_path}")
