# ✅ 설치 (한 번만 실행하면 됩니다)
# 터미널이나 Jupyter/Colab 환경에서 실행
# !pip install sentence-transformers
#pip install sentence-transformers
from sentence_transformers import SentenceTransformer, util
import re

def detect_language_with_threshold(text, threshold=0.7):
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = korean_chars + english_chars

    if total_chars == 0:
        return "Unknown"

    korean_ratio = korean_chars / total_chars
    english_ratio = english_chars / total_chars

    if korean_ratio >= threshold:
        return "Korean"
    elif english_ratio >= threshold:
        return "English"
    else:
        return "Mixed"

# 적절한 모델 선택
def get_model_for_language(text):
    language = detect_language_with_threshold(text)
    
    model_dict = {
        "Korean": "nunlp/KR-SBERT-V40K-klueNLI-augSTS",
        "English": "all-mpnet-base-v2",
        "Mixed": "paraphrase-MiniLM-L6-v2"
    }
    
    model_name = model_dict.get(language, "all-mpnet-base-v2")  # 기본값 English 모델
    model = SentenceTransformer(model_name)
    return model, language


# ✅ 2. 비교할 문장 정의
sentence1 = "aaaaaa"
sentence2 = "aaaaaa"

model , detected_lang = get_model_for_language(sentence1)

# ✅ 3. 문장을 임베딩(숫자 벡터)으로 변환
embedding1 = model.encode(sentence1, convert_to_tensor=True)
embedding2 = model.encode(sentence2, convert_to_tensor=True)

# ✅ 4. 코사인 유사도 계산 (문장의 의미 기반)
similarity = util.pytorch_cos_sim(embedding1, embedding2)

# ✅ 5. 결과 출력
print(f"문장 유사도 (코사인 유사도): {similarity.item():.4f}")

