# 파일 열기
f = open('C:/GitHub/JeoninHighSchool/수업예제/class9/t1.txt', 'w')
 #C:/GitHub/JeoninHighSchool/수업예제/class9/t1.txt
# 파일에 텍스트 쓰기
f.write('안녕하세요')
f.write('\n파일 쓰기 테스트 중 입니다.')
# 파일 닫기
f.close()
f = open('C:/GitHub/JeoninHighSchool/수업예제/class9/t1.txt', 'r')
print(f.read())
f.close()
