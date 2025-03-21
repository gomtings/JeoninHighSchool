"""
name = ""
stu_num = 0
            
name = input("이름을 입력해 주세요.")
stu_num = int(input("학번을 입력해 주세요."))

print('제 이름은 : {} 이고 학번은 : {} 입니다.'.format(name,stu_num))

#======================

name = input("이름을 입력해 주세요.")
if name == 'hello':
    a = int(input("나이를 입력해 주세요"))
elif name == 'world': 
    a = int(input("학번을 입력해 주세요."))
else:
    print("잘못된 입력 입니다.")       

"""

a = []
b = []
for elem in range(100):
    if elem % 4 == 0:
        a.append(elem)
    else:
        b.append(elem)
print("4의 배수", a)
print("그 외 숫자", b)    

a = []
b = []
elem = 0

while elem < 100:
    if elem % 4 == 0:
        a.append(elem)
    else:
        b.append(elem)
    elem += 1

print("4의 배수", a)
print("그 외 숫자", b)