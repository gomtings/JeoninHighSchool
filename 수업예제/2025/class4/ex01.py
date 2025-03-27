students = []
scores = []

# 학생 이름과 점수 입력
for _ in range(5):
    while True:
        data = input("학생 이름과 점수를 입력하세요 (예: 개 85): ")
        name, score = data.split()
        score = int(score)
        if 0 <= score <= 100:
            students.append(name)
            scores.append(score)
            break
        else:
            print("점수는 0에서 100 사이여야 합니다. 다시 입력해주세요.")

# 평균 점수 계산
average = sum(scores) / len(scores)
print("평균 점수:", average)

# 최고 점수 찾기
max_score = max(scores)
max_index = scores.index(max_score)
print(f"최고 점수를 받은 학생: {students[max_index]} ({max_score}점)")

# 60점 이상 합격자 출력
pass_students = [students[i] for i in range(len(scores)) if scores[i] >= 60]
print("60점 이상 합격자:", ", ".join(pass_students))