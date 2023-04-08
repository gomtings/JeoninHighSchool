class Bank():
    Number = 12345
    def __init__(self, Number, Balance):
        self.Number = Number #계좌번호
        self.Balance = Balance #잔액

    def deposit(self, money):
        self.Balance += money
        print("현재 잔액은:",self.Balance)
        

    def Withdrawal(self, money):
        if (self.Balance - money) > 0:
            self.Balance -= money
            print("현재 잔액은:",self.Balance)
        else:
            print("출금하려는 금액보다 잔액이 적습니다.")


    def inquiry(self, Number):
        Number = input("계좌번호를 입력해주세요.")
        if Number == 12345:
            print("현재 잔액은:",self.Balance)
        else:
            print("계좌가 존재하지 않습니다. 계좌를 만든 뒤 다시 시도해주세요.")


myBank = Bank(Number= 1234, Balance=0)
while True :
    print()
    message = input("무엇을 도와드릴까요? 입금(i), 출금(u),i 종료(x)\n>>>")

    if message == "입금" or message == "i" :
        amount = input("얼마를 입금하시겠습니까?\n>>>")
        try :
            amount = int(amount)
        except :
            print("잘못된 값을 입력하셨습니다.")
        else :
            if amount <= 0 :
                print("0보다 작으면 안됨.")
            else :
                myBank.deposit(int(amount))
    elif message == "출금" or message == "2" :
        amount = input("얼마를 출금하시겠습니까?\n>>>")
        try :
            amount = int(amount)
        except :
            print("잘못된 값을 입력하셨습니다.")
        else :
            if amount <= 0 :
                print("0보다 작으면 안됨.")
            elif amount > myBank.balance :
                print(f"님 돈 없어요 ㅋㅋ;;;. 현재 잔액은 {myBank.balance}원입니다.")
            else :
                myBank.withdraw(int(amount))
    elif message == "종료" or message == "4" :
        print("이용 땡큐.")
        break
    else :
        print("잘못된 값을 입력하셨습니다.")
