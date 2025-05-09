from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

# 기준 정답과 학생 답안
ref_answer = "Social media allows us to communicate with others quickly."
student_answer = "We can talk to people fast using social media."

# 임베딩
emb1 = model.encode(ref_answer, convert_to_tensor=True)
emb2 = model.encode(student_answer, convert_to_tensor=True)

# 유사도 측정
similarity = util.pytorch_cos_sim(emb1, emb2)
print(f"유사도: {similarity.item():.2f}")
