import time
mon=10000
class bank:
    def inside(money,x):
        money+=int(x)
        return money
    def outside(money,y):
        money-=y
        return(money)
    def cheek(money):
        print("현제 계좌에 있는 돈은 돈은 "+str(money)+"입니다")
while True:
    z=str(input("은행 서비스에 오신걸 환영합니다.\n_______________________________\n원하시는 서비스의 번호를 입력해주세요\n1.입금\n2.출금\n3.잔액조회\n아무키 취소"))
    if z=="1":
        mon=bank.inside(mon,input("입금하실 금액을 입력 해주세요"))
        print("입금이 완료되었습니다")
        time.sleep(0.5)
    elif z=="2":
        a=int(input("출금을 원하시는 금액을 입력해주세요"))
        if mon<a:
            if input("현제 계좌에는 "+str(mon)+"있기에 출금이 불가한 금액입니다.\n계자에 있는 돈을 모두 출금 합니까?\n1.확인\n2.취소")=="1":
                print(str(mon)+"만큼 출금 되었습니다.")
                mon=0
                time.sleep(0.5)
            else:
                print("취소되었습니다.")
                time.sleep(0.5)
        else:
            mon=bank.outside(mon,a)
            print("남은 금액은 "+int(mon)+" 입니다")
    elif z=="3":
        bank.cheek(mon)
        time.sleep(0.5)
    else:
        break
    