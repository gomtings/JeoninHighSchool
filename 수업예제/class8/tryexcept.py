"""
int a(){
    a= 1;
    b= 2;
    return a/b;
}
def a():
    a = 4
    b = 1
    return a/b

print(a())

b = 2
c = 1
print(b/C)
a = [10, 20, 30]
print(a[2])

def a(c):
    a = [10, 20, 30]
    a.remove(c)
    return a
print(a(4))
mydict = {'Kim': 1, 'Lee': 2}
print(mydict.get('Park'))

def a(a,c):
    return a+c
b = 1
c = 2
print(a(b,c))
f= open('exe.txt', 'r')
f= open('ex.txt', 'r')
try:
    print(a(c,d))
except ZeroDivisionError :
    print("오류남!!!") 
    
    def a(c,d):
        if(c==0 or d==0):
        print("0으로 나눌수 없습니다.")
    return c/d
c = int(input("c 입력"))
d = int(input("d 입력"))
print(a(c,d))

class User_Error(Exception):    # Exception을 상속받아서 새로운 예외를 만듦
    def __init__(self):
        super().__init__('결과가  0 보다 작습니다!!')
def a(c,d):
    return c/d
try:
    c = int(input("c 입력"))
    d = int(input("d 입력"))
    z = a(c,d)
    if(z < 1):
        raise User_Error
except  Exception as e:
    print(e)
"""
def a(c,d):
    return c/d
try:
    c = int(input("c 입력"))
    d = int(input("d 입력"))
    print(a(c,d))
except ZeroDivisionError: 
    print("ZeroDivisionError!!!")
except ValueError:
    print("ValueError!!!")
else:
    print("에러 없음!")
finally:
    print("hello world")
    
