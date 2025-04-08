# 사용자로부터 문자열 입력 받기
user_input = input("문자열을 입력하세요: ")

# 문자열 길이 계산
length = len(user_input)

# 모음 개수 계산 (소문자와 대문자 모두 포함)
vowels = "aeiouAEIOU"
vowel_count = 0
for char in user_input:
    if char in vowels:
        vowel_count += 1

# 공백 개수 계산
space_count = 0
for char in user_input:
    if char == " ":
        space_count += 1

# 문자열 뒤집기
reversed_string = user_input[::-1]

# 결과 출력
print("\n분석 결과:")
print(f"- 문자열 길이: {length}")
print(f"- 모음 개수: {vowel_count}")
print(f"- 공백 개수: {space_count}")
print(f"- 뒤집은 문자열: {reversed_string}")
