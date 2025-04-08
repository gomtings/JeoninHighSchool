# 사용자로부터 수 입력받기
n = int(input("피보나치 수열의 몇 개의 숫자를 출력할까요? (양의 정수 입력): "))

# 피보나치 수열 리스트 초기화
fibonacci = [0, 1]

# n이 1일 경우 첫 번째 숫자만 출력
if n == 1:
    print(f"피보나치 수열: {[fibonacci[0]]}")
# n이 2 이상일 경우 수열 계산 및 출력
elif n > 1:
    for i in range(2, n):
        next_number = fibonacci[i - 1] + fibonacci[i - 2]  # 이전 두 숫자의 합
        fibonacci.append(next_number)
    print(f"피보나치 수열: {fibonacci}")
else:
    print("올바른 양의 정수를 입력해주세요.")
