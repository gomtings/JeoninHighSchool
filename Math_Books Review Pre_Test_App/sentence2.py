import re

from difflib import SequenceMatcher

 

# 문자열 전처리 함수

def preprocess(text):

# 한글, 숫자, 알파벳 외의 모든 문자 제거

    text = re.sub(r'[^가-힣a-zA-Z0-9]', '', text)

    # 공백 제거

    text = text.replace(" ", "")

    return text

 

    # 두 한글 문자열을 정의

str1 = "나는 자택으로 돌아간다."

str2 = "나는 거처로 향한다."

 

# 전처리된 문자열

str1_processed = preprocess(str1)

str2_processed = preprocess(str2)

 

# SequenceMatcher 객체 생성

matcher = SequenceMatcher(None, str1_processed, str2_processed)

 

# 유사도 비율 계산

similarity_ratio = matcher.ratio()

 

print(f"전처리된 문자열의 유사도 비율: {similarity_ratio:.2f}")