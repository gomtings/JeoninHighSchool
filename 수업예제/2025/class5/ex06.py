# 사용자로부터 문자열 입력 받기
text = input("문자열을 입력하세요: ")

# 빈도수 계산을 위한 딕셔너리 초기화
char_frequency = {}

# 각 글자 빈도수 세기
for char in text:
    if char != " ":  # 공백 제외
        char_frequency[char] = char_frequency.get(char, 0) + 1

# 결과 출력
print("\n글자 빈도수:")
for char, count in char_frequency.items():
    print(f"{char}: {count}회")
