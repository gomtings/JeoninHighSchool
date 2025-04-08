# 과일 목록 생성
fruits = ["사과", "바나나", "체리", "딸기", "포도"]

# 사용자 입력 받기
user_fruit = input("좋아하는 과일을 입력하세요: ")

# 조건문으로 과일이 목록에 있는지 확인
if user_fruit in fruits:
    print(f"{user_fruit}(은)는 목록에 있습니다!")
else:
    print(f"{user_fruit}(은)는 목록에 없습니다. 목록에 추가합니다.")
    fruits.append(user_fruit)

# 반복문으로 과일 목록 출력
print("\n현재 과일 목록:")
for fruit in fruits:
    print(f"- {fruit}")

# 리스트 요소 중 특정 조건 충족 확인 (예: 이름이 두 글자인 과일 출력)
print("\n이름이 두 글자인 과일:")
for fruit in fruits:
    if len(fruit) == 2:  # 이름 길이가 2인 경우
        print(f"- {fruit}")
