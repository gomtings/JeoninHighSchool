# 사용자로부터 입력받기
numbers = input("숫자를 공백으로 구분하여 입력하세요: ").split()

# 문자열 리스트를 정수 리스트로 변환
numbers = [int(num) for num in numbers]

# 짝수와 홀수를 저장할 리스트 초기화
evens = []
odds = []

# 짝수와 홀수 분류
for num in numbers:
    if num % 2 == 0:
        evens.append(num)
    else:
        odds.append(num)

# 짝수와 홀수의 합 계산
sum_evens = sum(evens)
sum_odds = sum(odds)

# 결과 출력
print(f"짝수의 합: {sum_evens}")
print(f"홀수의 합: {sum_odds}")
