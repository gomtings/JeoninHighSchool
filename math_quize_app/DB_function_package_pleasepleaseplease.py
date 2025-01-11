import pymysql
import json

# DB 접속 함수 (따로 꺼내 쓸 일은 없을듯.)
def connect_to_database():
    try:
        # DB 접속
        db = pymysql.connect(host='solimatics@localhost', port=3306, user="solimatics",
                             passwd="dudrnr68*", db='math101', charset='utf8')
        print('DB 연결 성공')
        return db
    except pymysql.Error as e:
        print(f'DB 연결 실패: {e}')
        return None

    
# DB 접속 해제 함수 (이것도 따로 꺼내 쓸 일 X)
def close_connection():
    db = pymysql.connect(host='solimatics@localhost', port=3306, user="solimatics",
                             passwd="dudrnr68*", db='math101', charset='utf8')
    # DB 연결 닫기
    db.close()

    
    

# DB에 데이터 추가하는 함수. 밑에 'new_data' 있는 정보를 DB에 삽입.
def insert_data(data):
    # DB 연결
    db = connect_to_database()
    # 커서 가져오기 (쿼리 실행하기 위함)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    for data in new_data:
        select_query = "SELECT COUNT(*) AS count FROM book WHERE book_num = %s AND question = %s"  
        cursor.execute(select_query, (data['book_num'], data['question']))
        count_result = cursor.fetchone()
        count = count_result['count']
        if count == 0:
            insert_query = "INSERT INTO book VALUES(%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (
                data['book_num'], data['question'], data['c_answer'], data['f_answer1'], data['f_answer2'], data['f_answer3']
            ))

    db.commit()
    # DB 연결 종료
    close_connection()

    
    
# 책 번호를 기준으로 DB 정보 삭제. ex) delete_data_bn('2')은 2번 책 문제 전체 삭제
def delete_data_bn(book_num):
    # DB 연결
    db = connect_to_database()
    # 커서 가져오기 (쿼리 실행하기 위함)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    delete_query = "DELETE FROM book WHERE book_num = %s"
    cursor.execute(delete_query, (book_num,))
    db.commit()
    # DB 연결 종료
    close_connection()

    
    
    
# 문제를 기준으로 DB정보 삭제
def delete_data_qn(question):
    # DB 연결
    db = connect_to_database()
    # 커서 가져오기 (쿼리 실행하기 위함)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    delete_query = "DELETE FROM book WHERE question = %s"
    cursor.execute(delete_query, (question,))
    db.commit()
    # DB 연결 종료
    close_connection()

    
    
    
    
# DB 데이터 불러오기 함수
def fetch_data():
    # DB 연결
    db = connect_to_database()
    # 커서 가져오기 (쿼리 실행하기 위함)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    select_query = "SELECT * FROM book"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    
    big_dic = {}
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
    
    # DB 연결 종료
    close_connection()
    
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
# insert_data(new_data)


# 책 번호로 삭제하기
#delete_data_bn('1')


# 질문 이름으로 삭제하기
# delete_data_qn('Q2')


# 데이터 불러오기
data = connect_to_database()




print(data)













# 1. db 인자로 안받아도 되게끔 만들어 clear         
# 2. 접속여부 확인 (try catch문) clear
# 3. 예외 처리(접속 안될 경우?) --> 출력 clear
