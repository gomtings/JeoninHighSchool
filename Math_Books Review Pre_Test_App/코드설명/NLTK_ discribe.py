# NLTK

# NLTK(Natural Language Toolkit)이다. 자연어 처리 즉 (NLP, Natural Language Processing)를 수행하는 데 널리 사용되는 라이브러리이다. 
# NLTK는 텍스트 데이터의 처리와 분석을 위한 다양한 도구와 리소스를 제공한다.

# NLTK의 주요 기능

# 1. 토큰화(Tokenization) : 텍스트를 단어 또는 문장 단위로 나누는 과정이다다

import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt')
text = "Hello, how are you?" #"Hello, how are you?"라는 문장을 단어 단위로 나누면
tokens = word_tokenize(text)
print(tokens) #['Hello', 'how', 'are', 'you', '?']와 같은 결과를 얻을 수 있습니다.

# 2. 품사 태깅(Part-of-Speech Tagging) : 각 단어가 문장에서 어떤 품사를 가지고 있는지 태깅하는 작업이다.
# 태깅(Tagging)은 관련된 키워드나 정보를 추가하는 작업이다.

from nltk import pos_tag
from nltk.tokenize import word_tokenize

text = "The cat sleeps" #"The cat sleeps"에서 관사(Det),d "cat"은 명사(Noun), "sleeps"는 동사(Verb)로 태깅된다.
tokens = word_tokenize(text)
tagged = pos_tag(tokens)
print(tagged) #결과 값 : [('The', 'DT'), ('cat', 'NN'), ('sleeps', 'NNS')]


# 3. 개체명 인식(Named Entity Recognition, NER) : 텍스트에서 사람, 장소, 날짜 등의 고유명사를 인식하는 작업이다.


#영어를 쓸때때
from nltk import ne_chunk
from nltk.tokenize import word_tokenize

text = "Barack Obama was born in Hawaii."
tokens = word_tokenize(text)
tagged = pos_tag(tokens) #pos_tag는 영어 자연어 처리 중심으로 개발되었다. 그러므로 영어 전용이기에 한국어는 작동하지 않는다.
tree = ne_chunk(tagged)
print(tree)

#한국어를 쓸때
from konlpy.tag import Okt #한국어는 구조가 영어와 다르기 때문에, KoNLPy 같은 한국어 전용 라이브러리를 사용해야한다.
#예를 들어 Okt, Komoran, Mecab, Hannanum, Kkma 등이 있다.
okt = Okt()

text = "삼성전자가 오늘 주가가 상승했다."
pos_result = okt.pos(text)

print(pos_result) #결과 : [('삼성전자', 'Noun'), ('가', 'Josa'), ('오늘', 'Noun'), ('주가', 'Noun'), ('가', 'Josa'), ('상승', 'Noun'), ('했다', 'Verb'), ('.', 'Punctuation')]

# 4. 어간 추출(Stemmer : 단어를 그 어근으로 변환하는 작업이다.
#예를 들어 "running" 을 "run"으로 변환하는 등의 작업을 한다.
#nltk에서는 PorterStemmer, LancasterStemmer와 같은 여러 어간 추출기를 제공한다.
# 여기서 어간 추출(Stemmer)은 단어를 그 기본형태(어간)으로 단순하게 줄여주는 작업니다.
#ex) running -> run
#    flies -> fli
#    happily -> happili 이렇게 종종 사전에 없는 어형을 만들어낸다.

'''
1.PorterStemmer : 일반적인 텍스트 처리에 적합(검색엔진, 간단한 NLP등)

특징: 보수적, 변화가 적음
장점: 일반적으로 덜 과격해서 원형을 유지하려는 경우에 적합

사용 예시

from nltk.stem import PorterStemmer

stemmer = PorterStemmer()
print(stemmer.stem("running"))   결과 : run
print(stemmer.stem("flies"))     결과 : fli
print(stemmer.stem("happiness")) 결과 : happi

2.LancasterStemmer 많은 변형이 있는 단어들을 뭉뚱그릴 때 좋지만, 의미 왜곡 위험 있음

특징: 공격적, 많이 줄임
장점: 간단하고 일관되게 많이 줄여줌
단점: 과도하게 줄이기도 해서 의미 손실 위험 있음

사용 예시

from nltk.stem import LancasterStemmer

stemmer = LancasterStemmer()
print(stemmer.stem("running"))     결과: run
print(stemmer.stem("flies"))       결과: fly
print(stemmer.stem("happiness"))   결과: happy
print(stemmer.stem("maximum"))     결과: maxim
print(stemmer.stem("crying"))      결과: cry

'''

from nltk.stem import PorterStemmer

ps = PorterStemmer()
print(ps.stem("running"))  #결과 : 'run'

# 5. 표제어 추출(Lemmatization) : 어간 추출과 비숫하지만, 더 정교하게 의미를 고려하여 단어를 표제어(lemma)로 변환한다.
# 예를 들어 "better"은 "good"으로, "running"은 "run"으로 변환된다.

from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
print(lemmatizer.lemmatize("better", pos="a"))  #결과: 'good'

# 6. 텍스트 분류(Text Classification) : NLTK에서는 텍스틀 분류하는 데 사용할 수 있는 다양한 알고리즘을 제공한다.
# 예를 들어, 나이브 베이즈 분류기(Naive Bayes Classifier)를 사용할 수 있다.

'''
나이브 베이즈 분류기(Naive Bayes Classifier) : 통계학과 확률이론을 바탕으로 한 지도 학습 분류 알고리즘이다.
특히 텍스트 분류 문제(예: 스팸 메일 분류, 감정 분석 등)에 널리 쓰이는 아주 빠르고 간단한 모델이다.r

Bayes' Theorem(베이즈 정리)를 기반으로 하고, Naive(순진한) 가정: 모든 특성(단어들)이 서로 독립이라는 가정을 한다.
✅ 베이즈 정리 기본 공식: 


'''
