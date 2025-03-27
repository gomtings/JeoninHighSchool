text = input("텍스트를 입력하세요: ")

# 총 길이
total_length = len(text)
print("총 길이:", total_length)

# 단어 개수
words = text.split()
print("단어 개수:", len(words))

# 가장 많이 등장한 문자
from collections import Counter
text_no_space = text.replace(" ", "")
char_count = Counter(text_no_space)
most_common_char = char_count.most_common(1)[0]
print(f"가장 많이 등장한 문자: {most_common_char[0]} ({most_common_char[1]}회)")

# 각 문자의 등장 횟수
print("문자별 등장 횟수:")
for char, count in char_count.items():
    print(f"{char}: {count}회")
