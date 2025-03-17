"""
=================================================
* Project      :  은행 계좌 만들기...
* Description  : 은행 계좌 만들기...
* Author       : Lee Sang Woo
* Date         : 2023-03-24
* Version      : 1.0 
===================* History *===================
*  2023-03-24 init 최초 생성...
"""

class bank:
    def __init__(self):
        self.error_chk = False
        self.account_number = ""
        self.client_pw = ""
        self.Balance = 0
        self.account_info = {self.account_number:self.client_pw}
        self.client_info = {self.client_pw:self.Balance}
    def account_number_set(self):
        while True:
            try :
                account = str(input('생성할 계좌번호를 입력하세요.'))
                if account != "":
                    if account in self.account_info:
                        print("이미 있는 계좌 번호 입니다.")
                    else:
                        while True:
                            password = str(input('사용하실 계좌 비밀번호를 입력하세요.'))
                            if password != "":
                                password2 = str(input('비밀번호를 다시 입력해 주세요.'))
                                if password == password2:
                                    self.account_info[account] = password
                                    self.client_info[password] = 0
                                    self.account_number = account
                                    self.Balance = 0
                                    print("고객님의 계좌 번호는 {} 이며 계좌의 잔액은: {} 원 입니다.".format(account,0))
                                    self.error_chk = False
                                    break
                                else:
                                    print("입력이 바르지 않습니다 다시 입력해 주세요.")
                                    self.error_chk = True
                        break            
                else:
                    print("입력이 바르지 않습니다 다시 입력해 주세요.")
                    self.error_chk = True
            except :
                print("오류가 발생 했습니다 다시 입력해 주세요.")
                self.error_chk = True     
        return self.error_chk
    def Deposit(self) :
        try :
            account = str(input('입급하실 계좌 번호를 입력하세요.'))
            if account in self.account_info:
                for err_cnt in range(0,5):
                    password = str(input('계좌 비밀번호를 입력하세요.'))
                    if password == self.account_info.get(account) :
                        bal = int(input('입급하실  금액을 입력해 주세요.'))
                        value = self.client_info.get(password)
                        value = value+bal
                        self.client_info[password] = value
                        self.Balance = value
                        self.account_number = account
                        print("입금 후 계좌 {} 의 잔액은 {} 원 입니다.".format(self.account_number,self.Balance))
                        self.error_chk = False
                        break
                    else:    
                        print("입력이 바르지 않습니다 다시 입력해 주세요. 에러 카운트 {} / {}".format((err_cnt+1),5))
                        self.error_chk = True
            else:
                print("존재하지 않는 계좌 번호 입니다.")
                self.error_chk = True
        except :
            print("오류가 발생 했습니다 다시 입력해 주세요.")
            self.error_chk = True
        return self.error_chk
    def Withdrawal(self) :
        try :
            account = str(input('출금하실 계좌 번호를 입력하세요.'))
            if account in self.account_info:
                for err_cnt in range(0,5):
                    password = str(input('계좌 비밀번호를 입력하세요.'))
                    if password == self.account_info.get(account) :
                        while True :
                            value = self.client_info.get(password)
                            if value == 0:
                                print("잔액이 부족 합니다. 현재 잔액은{} 입니다.".format(value))
                                break
                            bal = int(input('출금하실  금액을 입력해 주세요.'))
                            if bal > value :
                                print("잔액이 바르지 않습니다 현재 잔액은{} 입니다.".format(value))
                                pass
                            else:    
                                value -= bal
                                self.client_info[password] = value
                                self.Balance = value
                                self.account_number = account
                                print("입금 후 계좌 {} 의 잔액은 {} 원 입니다.".format(self.account_number,self.Balance))
                                self.error_chk = False
                                break
                    else:    
                        print("입력이 바르지 않습니다 다시 입력해 주세요. 에러 카운트 {} / {}".format((err_cnt+1),5))
                        self.error_chk = True
                    break    
            else:
                print("존재하지 않는 계좌 번호 입니다.")
                self.error_chk = True
        except :
            print("오류가 발생 했습니다 다시 입력해 주세요.")
            self.error_chk = True
        return self.error_chk
    def Balance_check(self):
        try :
            account = str(input('조회 하실 계좌 번호를 입력하세요.'))
            if account in self.account_info:
                for err_cnt in range(0,5):
                    password = str(input('계좌 비밀번호를 입력하세요.'))
                    if password == self.account_info.get(account) :
                        value = self.client_info.get(password)
                        print("요청하신 계좌 {} 의 잔액은 {} 원 입니다.".format(account,value))
                        self.error_chk = False
                        break
                    else:
                        print("입력이 바르지 않습니다 다시 입력해 주세요. 에러 카운트 {} / {}".format((err_cnt+1),5))
                        self.error_chk = True
            else:
                print("존재하지 않는 계좌 번호 입니다.")
                self.error_chk = True
        except :
            print("오류가 발생 했습니다 다시 입력해 주세요.")
            self.error_chk = True 
        return self.error_chk      
if __name__ == "__main__":
    my_bank = bank()
    while True:
        try :
            print("\n===========================================================================")
            print("사용하실 서비스 번호를 입력해 주세요. 1 : 계좌계설 2: 입금 3: 출금 4 : 잔액조회 ")
            print("그만 이용 하시려면 5 번을 입력해 주세요.")
            service = int(input("입력 ="))
            print("===========================================================================\n")
            if service == 1:
                if my_bank.account_number_set():
                    print("에러가 발생하였습니다. 다음에 다시 이용해 주세요.")
                else:
                    pass      
            elif service == 2:
                if my_bank.Deposit():
                    print("에러가 발생하였습니다. 다음에 다시 이용해 주세요.")
                else:
                    pass 
            elif service == 3:        
                if my_bank.Withdrawal():
                    print("에러가 발생하였습니다. 다음에 다시 이용해 주세요.")
                else:
                    pass
            elif service == 4:
                if my_bank.Balance_check():
                    print("에러가 발생하였습니다. 다음에 다시 이용해 주세요.")
                else:
                    pass
            elif service == 5:
                print("이용해 주셔 감사합니다.")
                break
            else:
                print("입력이 바르지 않습니다 다시 입력해 주세요.") 
            
        except :
            print("오류가 발생 했습니다 다시 입력해 주세요.") 

