
import sys

def calculate_score_from_answers(answer_string):
    # 예/아니오를 ,로 구분한 문자열로 받음: "예,아니오,예,예,아니오"
    answers = answer_string.strip().split(',')
    score = sum(20 for a in answers if a.strip() == '예')
    print(f"{score}")  # 점수만 출력 (SpringBoot가 읽게)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("입력된 답변이 없습니다. 예: python calculate_question_score.py 예,아니오,예,예,아니오")
        sys.exit(1)

    input_answers = sys.argv[1]
    calculate_score_from_answers(input_answers)
