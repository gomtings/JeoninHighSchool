# 배열의 크기 입력받기
n = int(input("배열의 크기를 입력하세요: "))

# 빈 배열 초기화
numbers = []

# 배열에 값 입력받기
for i in range(n):
    num = int(input(f"{i + 1}번째 숫자를 입력하세요: "))
    numbers.append(num)

# 결과 출력
print("입력받은 배열:", numbers)
