import requests
import json

# DB에 데이터 추가하는 함수. 밑에 'new_data' 있는 정보를 DB에 삽입.
def insert_data(data):
    for new_data in data:
        post = {'book_num': new_data['book_num'], 'question': new_data['question'],'c_answer': new_data['c_answer'],'f_answer1': new_data['f_answer1'],'f_answer2': new_data['f_answer2'],'f_answer3': new_data['f_answer3']}
        response = requests.post('http://tkddn4508.dothome.co.kr/math101/insert_data.php', data=post)
    print(response)

# 책 번호를 기준으로 DB 정보 삭제. ex) delete_data_bn('2')은 2번 책 문제 전체 삭제
def delete_data_bn(book_num):
    post = {'book_num': book_num}
    response = requests.post('http://tkddn4508.dothome.co.kr/math101/delete_data_bn.php', data=post)

# 문제를 기준으로 DB정보 삭제
def delete_data_qn(question):
    post = {'question': question}
    response = requests.post('http://tkddn4508.dothome.co.kr/math101/delete_data_qn.php',data=post)

# DB 데이터 불러오기 함수
def fetch_data():
    # DB 연결
    # 커서 가져오기 (쿼리 실행하기 위함)
    response = requests.get('http://tkddn4508.dothome.co.kr/math101/fetch_data.php')
    json_msg = json.loads(response.text)
    big_dic = {}
    if json_msg['result'] == 'success':
        rows = json_msg['row']
        for row in rows:
            book_num = row['book_num']
            question = row['question']
            c_answer = row['c_answer']
            f_answer1 = row['f_answer1']
            f_answer2 = row['f_answer2']
            f_answer3 = row['f_answer3']
        
            if book_num not in big_dic:
                big_dic[book_num] = {}
        
            if question not in big_dic[book_num]:
                big_dic[book_num][question] = {}
        
            big_dic[book_num][question]['정답'] = c_answer
            big_dic[book_num][question]['오답'] = [f_answer1, f_answer2, f_answer3]
    else:
        # 연결 실패 처리
        return False
    return big_dic

# ======================== 실행 예시 ======================== #

new_data = [
    {'book_num': '01', 'question': 'Q1', 'c_answer': '답1', 'f_answer1': '답2', 'f_answer2': '답3', 'f_answer3': '답4'},
    {'book_num': '01', 'question': 'Q2', 'c_answer': '답1', 'f_answer1': '답2', 'f_answer2': '답3', 'f_answer3': '답4'},
    {'book_num': '01', 'question': 'Q3', 'c_answer': '답1', 'f_answer1': '답2', 'f_answer2': '답3', 'f_answer3': '답4'},
    {'book_num': '01', 'question': 'Q4', 'c_answer': '답1', 'f_answer1': '답2', 'f_answer2': '답3', 'f_answer3': '답4'},
    {'book_num': '01', 'question': 'Q5', 'c_answer': '답1', 'f_answer1': '답2', 'f_answer2': '답3', 'f_answer3': '답4'},
    {'book_num': '02', 'question': '칸토어가 "____" 을 처음 발표할 때 수학계의 거센 반론을 받았다.', 'c_answer': '집합론', 'f_answer1': '밴다이어그램', 'f_answer2': '조건제시법', 'f_answer3': '상대성이론'},
    {'book_num': '02', 'question': '칸토어의 국적은 "____"이다.', 'c_answer': '독일', 'f_answer1': '러시아', 'f_answer2': '프랑스', 'f_answer3': '덴마크'},
    {'book_num': '02', 'question': '다음 중 집합이 될 수 없는 경우는?', 'c_answer': '귀여운 동물들의 집합', 'f_answer1': '이름이 세 글자인 동물들의 집합', 'f_answer2': '조류의 집합', 'f_answer3': '물 속에 사는 동물들의 집합'},
    {'book_num': '02', 'question': 'C={1,2,3}의 부분잡합의 개수는?', 'c_answer': '8개', 'f_answer1': '6개', 'f_answer2': '9개', 'f_answer3': '7개'},
    {'book_num': '02', 'question': '다음 중 설명이 올바르지 않은 것은?', 'c_answer': '공집합 = 0만을 원소로 가지는 집합', 'f_answer1': '무한집합 = 원소의 개수가 무한한 집합', 'f_answer2': '합집합 AUB = 집합 A에 속하거나 집합 B에 속하는 모든 원소의 집합', 'f_answer3':  '차집합 A-B = 집합 A에는 속하지만 집합 B에는 속하지 않는 모든 원소의 집합'}
]


# 데이터 추가하기
insert_data(new_data)


# 책 번호로 삭제하기
#delete_data_bn('1')


# 질문 이름으로 삭제하기
# delete_data_qn('Q2')


# 데이터 불러오기

#value = insert_data()
#print(value)
