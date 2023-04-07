number = {'66997744': 100000,'774466':20000}
print(number["66997744"])
class bank():   #입금,출금,잔액
    def __init__(self,n):
        self.deposit = 0 
        self.withdraw = 0
        self.number = n
        

    def dep(self,de):   #입금
        if de > 0:
            self.deposit = de
            n = input("계좌번호 입력")
            if(n in self.number):
                self.number[n] += self.deposit
            else:
                print("계좌 번호가 없네요")
                return "TT"
            #self.balance = self.balance + self.deposit
            #bank.bal()
            print(f"{self.deposit}원이 입금되었습니다")
            print(f"통장 잔액{self.number[n]}원")

    def wit(self,withd):    #출금
        if withd > 0:
            self.withdraw = withd
            n = input("계좌번호 입력")
            if(n in self.number):
                if(self.number[n]-self.withdraw > 0 ):
                    self.number[n] -= self.withdraw
                    print(f"성공하였습니다 남은잔액{self.number[n]}")
                else:
                    print(f"잔액이 부족해 출금이 불가해요 남은 잔액{self.number[n]}")
            else:
                print("계좌 번호가 없네요")
                return "TT"

        
        #self.balance = self.balance - self.withdraw
        #if(self.balance >= 0):
        #    print("잔액이 부족해요")
        #else:
        #    print(f"{self.withdraw}원 출금되었습니다.")
        
    def bal(self):      #잔액확인
        #global balance
        n = input("확인하고 싶은 계좌번호 입력")
        if(n in self.number):
            print(f"{self.number[n]}원")
        else:
            print("계좌 번호가 없네요")
            return "TT"
        balance = self.number[n]
        
        #print(f"현재 잔액은{balance}입니다")
        return balance
run = bank(number)
while(True):
    a = input('어떤 기능을 사용하실 건가요? 입금(d,D) 출금(w,W) 잔액확인(b,B) 종료는(t)')

    if(a == 'd' or  a == 'D'):
        try:
            value = int(input("입금할 금액입력"))
            if value >= 0 and value <= 9: 
                run.dep(value)
            else:
                pass    
        except:
            pass
    elif(a == 'w' or  a == 'W'):
        run.wit(int(input("출금할 금액입력")))
    elif(a == 'b' or  a == 'B'):
        run.bal()
    if(a == 't'):
        break
