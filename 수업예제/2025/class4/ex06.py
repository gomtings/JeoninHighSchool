text = input("텍스트를 입력하세요: ")

# 총 길이
total_length = len(text)
print("총 길이:", total_length)

# 단어 개수
words = text.split()
print("단어 개수:", len(words))

# 가장 많이 등장한 문자
text_no_space = text.replace(" ", "")
char_count = {}
for char in text_no_space:
    char_count[char] = char_count.get(char, 0) + 1

# 가장 많이 등장한 문자 찾기
most_common_char = None
max_count = 0

for char, count in char_count.items():
    if count > max_count:
        most_common_char = char
        max_count = count

print(f"가장 많이 등장한 문자: {most_common_char} ({max_count}회)")

# 각 문자의 등장 횟수
print("문자별 등장 횟수:")
for char, count in char_count.items():
    print(f"{char}: {count}회")
