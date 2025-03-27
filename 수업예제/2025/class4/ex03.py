students = {}
for _ in range(10):
    name = input("학생 이름을 입력하세요: ")
    score = int(input(f"{name}의 점수를 입력하세요: "))
    students[name] = score

# 평균 점수 계산
average_score = sum(students.values()) / len(students)
print("전체 평균 점수:", average_score)

# 최고 점수와 학생 찾기
max_student = max(students, key=students.get)
print(f"가장 높은 성적: {max_student} ({students[max_student]}점)")

# 최저 점수와 학생 찾기
min_student = min(students, key=students.get)
print(f"가장 낮은 성적: {min_student} ({students[min_student]}점)")

# 50점 이상인 학생 리스트
pass_students = [name for name, score in students.items() if score >= 50]
print("50점 이상 학생:", ", ".join(pass_students))
