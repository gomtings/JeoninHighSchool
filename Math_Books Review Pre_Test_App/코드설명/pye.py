# import random

# answer = random.randint(1,10)

# guess = int(input("1부터 10까지 중 아무 숫자나 입력하시오"))

# if guess == answer:
#     print("정답입니다!")
# else:
#     print("틀렸습니다!")

while True:
    answer = input("김동현은?")
    
    if answer == "병신":
        print("네 맞습니다!")
        break
    else:
        print("아닙니다!!")
        