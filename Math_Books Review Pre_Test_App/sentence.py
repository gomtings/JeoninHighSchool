# ✅ 설치 (한 번만 실행하면 됩니다)
# 터미널이나 Jupyter/Colab 환경에서 실행
# !pip install sentence-transformers

from sentence_transformers import SentenceTransformer, util

# ✅ 1. 모델 로딩 (한국어에 특화된 KoSentence-BERT)
model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')

# ✅ 2. 비교할 문장 정의
sentence1 = "나는 자택으로 돌아간다"
sentence2 = "나는 거처로 향한다"

# ✅ 3. 문장을 임베딩(숫자 벡터)으로 변환
embedding1 = model.encode(sentence1, convert_to_tensor=True)
embedding2 = model.encode(sentence2, convert_to_tensor=True)

# ✅ 4. 코사인 유사도 계산 (문장의 의미 기반)
similarity = util.pytorch_cos_sim(embedding1, embedding2)

# ✅ 5. 결과 출력
print(f"문장 유사도 (코사인 유사도): {similarity.item():.4f}")
