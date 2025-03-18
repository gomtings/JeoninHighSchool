#조건문
#if 문
#if True:
#    print("조건이 True 니깐 실행됨")
#if False:
#    print("조건이 False 니깐 실행 안됨")

#if else 문
#if False:
#    print("조건이 False 니깐 실행 안됨")
#else:    
#    print("조건이 False 니깐 실행 안됨") 

#다중 조건문 (if, elif , else)   
"""
x = 100
if x <10:
    print(x)
elif x == 100:
    print(x)
else:    
    print(x)
"""
city = '춘천'
age = 20
if city in '춘천':
    if age >=20:
        print("참 입니다.")
    else:
        print("거짓 입니다.")   
else:
    print("지역이 춘천이 아닙니다.")
