import random

answer = random.randint(1, 100)

while True:
    guess = int(input("숫자를 맞혀 보세요 (1~100): "))
    if guess < answer:
        print("더 높게!")
    elif guess > answer:
        print("더 낮게!")
    else:
        print("정답입니다!")
        break
