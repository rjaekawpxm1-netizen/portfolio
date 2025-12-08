# analyze_and_recommend.py

import json
from predict_emotion_from_audio import predict_emotion_from_audio
from predict_emotion_from_video import predict_emotion_from_video
from recommend_songs import recommend_songs

def analyze_and_recommend():
    voice_score = predict_emotion_from_audio()
    face_score = predict_emotion_from_video()

    final_score = (voice_score + face_score) / 2

    if final_score >= 75:
        emotion = "Anger"
    elif final_score >= 50:
        emotion = "Anxiety"
    elif final_score >= 25:
        emotion = "Sadness"
    else:
        emotion = "Normal"

    songs = recommend_songs(emotion)

    result = {
        "face_score": face_score,
        "voice_score": voice_score,
        "final_score": final_score,
        "emotion": emotion,
        "recommended_songs": songs
    }

    print(json.dumps(result))

if __name__ == "__main__":
    analyze_and_recommend()
