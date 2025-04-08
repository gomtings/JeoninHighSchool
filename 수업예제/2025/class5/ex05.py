# 사용자로부터 단어 입력 받기
word = input("단어를 입력하세요: ")

# 팰린드롬 확인
if word == word[::-1]:  # 단어를 뒤집어서 비교
    print(f'"{word}"는 팰린드롬입니다!')
else:
    print(f'"{word}"는 팰린드롬이 아닙니다.')
