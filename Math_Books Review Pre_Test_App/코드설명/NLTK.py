# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from difflib import SequenceMatcher

# # nltk 자원 다운로드
# nltk.download('punkt')
# nltk.download('stopwords')

# # 정답 문장과 사용자 입력
# answer = "hello world"
# user_input = input("문장을 입력하세요: ")

# # 전처리 함수
# def preprocess(text):
#     stop_words = set(stopwords.words('english'))
#     tokens = word_tokenize(text.lower())
#     return [word for word in tokens if word.isalpha() and word not in stop_words]

# # 유사도 측정 함수 (간단한 문자열 유사도)
# def calculate_similarity(ref, test):
#     return SequenceMatcher(None, ref, test).ratio()

# # 전처리된 문장
# answer_tokens = preprocess(answer)
# user_tokens = preprocess(user_input)

# # 리스트를 문자열로 다시 합침 (SequenceMatcher는 문자열 비교 기반)
# answer_str = ' '.join(answer_tokens)
# user_str = ' '.join(user_tokens)

# # 유사도 계산
# similarity = calculate_similarity(answer_str, user_str)
# score = round(similarity * 100, 2)

# # 출력
# print(f"\n입력한 문장의 정답과 유사도: {score}%")

from konlpy.tag import Okt
from difflib import SequenceMatcher

# 형태소 분석기
okt = Okt()

# 전처리 함수
def preprocess(text):
    tokens = okt.morphs(text)
    return ' '.join(tokens)  # 문자열로 다시 변환

# 유사도 계산
def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 정답과 입력
answer = "두 변수의 x, y에 대하여 x의 값이 정해짐에에 따라 y의 값이 하나로 통해 정해지는 관계가 있는 것"
user_input = input("당신의 문장을 입력하세요: ")

# 전처리
answer_prep = preprocess(answer)
input_prep = preprocess(user_input)

# 유사도 계산
similarity = calculate_similarity(answer_prep, input_prep)
score = round(similarity * 100, 2)

# 결과 출력
print(f"\n정답과의 유사도: {score}%")
