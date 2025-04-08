# 사용자로부터 숫자로 이루어진 문자열 입력 받기
numbers = input("숫자로 이루어진 문자열을 입력하세요: ")

# 빈도수 계산을 위한 딕셔너리 초기화
frequency = {}

# 각 숫자 빈도수 세기
for num in numbers:
    if num.isdigit():  # 숫자만 처리
        frequency[num] = frequency.get(num, 0) + 1

# 결과 출력
print("\n숫자 빈도수:")
for num, count in frequency.items():
    print(f"{num}: {count}회")
