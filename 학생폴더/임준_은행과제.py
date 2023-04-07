#  은행계좌 
#  class 사용
#  입금, 출금, 잔액조회 기능
#  2023_04_07 수정

#balance = 0
class Bank():
    brr = None
    #global balance 
    

    def __init__(self):
        self.balance = 0

    def account(self):
        try:
            self.id = str(input("아이디: "))
            pw = str(input("비밀번호: "))
        except:
            pass
        if self.id == 'junlim' and pw == '1234':
            print("로그인 성공!")
            print("==========================")
            print("")
            print("")
            
            Bank.order()
        else:
            print("")
            print("")
            print("계정 불일치")
            err = input("다시 입력: r / 종료: q  --> ")
            if err >='a' and err <='z'or err >='A' and err <='Z':  
                if err == 'r' or err == 'R':
                    Bank.account()

                elif err == 'q' or err == 'Q':
                    print("종료합니다.")

                else:
                    pass
                
            

    def order(self): # 입출금 명령

        print(self.id, "님의 계좌:")
        print("")
        print("")
        Bank.balance_inquiry()
        print("")
        while True:
            brr = input("입금: d / 출금: w / 송금: s / 종료: q  --> ")
            if brr == 'd' or brr == 'D':
                Bank.desposit()
                print("")
                Bank.balance_inquiry()
                
            elif brr == 'w' or brr == 'W':
                Bank.withdraw()
                print("")
                Bank.balance_inquiry()


            elif brr == 's' or brr == 'S':
                Bank.remittance()
                print("")
                Bank.balance_inquiry()
                

            elif brr == 'q' or brr == 'Q':
                
                frr = input("종료: q / 로그아웃: l  --> ")

                if frr == 'l' or brr == 'L':
                    print("")
                    print("")
                    
                    Bank.account()
                    
                    
                elif brr == 'q' or brr == 'Q':
                    print("종료합니다.")
                
                break

            else:
                pass


                
        

    def balance_inquiry(self):  # 잔액조회
        
        print("현재 잔액:", self.balance)

    def desposit(self):  # 입금
        arr = int(input ("입금할 금액:"))
        self.balance += arr
        print("==========================")
        print("")
        print("")
        print(f"{arr}원이 입금되었습니다.")
        

    def withdraw(self): # 출금
        drr = int(input ("출금할 금액:"))
        grr = str(input("비밀번호를 입력해주세요: "))
        if grr == "1234":
            self.balance -= drr
            print("==========================")
            print("")
            print("")
            print(f"{drr}원이 출금되었습니다.")
        
        else: 
            hrr = str(input("비밀번호가 틀렸습니다.  다시입력: r  --> / 돌아가기: h   --> "))
            if hrr == 'r' or hrr == 'R':
                Bank.withdraw()
            elif hrr == 'h' or hrr == 'H':
                Bank.order()
            else: 
                pass

    def remittance(self):  # 송금
        irr = input("송금할 계좌를 입력해주세요:  ")
        jrr = int(input("송금할 금액을 입력해주세요:  "))

        grr = str(input("비밀번호를 입력해주세요: "))
        if grr == "1234":
            self.balance -= jrr
            print("==========================")
            print("")
            print("")
            print(f"[{irr}]님에게 {jrr}원이 송금되었습니다.")
        
        else: 
            hrr = str(input("비밀번호가 틀렸습니다.  다시입력: r / 돌아가기: h   --> "))
            if hrr == 'r' or hrr == 'R':
                Bank.withdraw()
            elif hrr == 'h' or hrr == 'H':
                Bank.order()
            else: 
                pass

        


Bank = Bank()
Bank.account()
