# 은행 계좌 class 만들기
# 입금, 출금, 잔액조회 기능 사용

class Bank() :
    def __init__(self, account_number) :
        self.account_number = account_number
        self.account = {"111-1111-1111-11" : 0, "123-1234-1234-12" : 100, "123-4567-8901-23" : 10000}
        self.balance = self.account[account_number]
    def if_account(self) :
        if self.account_number in self.account.keys() :
            return True
        else :
            return False
    def deposit(self, add_amount) : # 입금
        self.balance += add_amount
    def withdraw(self, remove_amount) : #출금
        self.balance -= remove_amount
    def get_balance(self) : #잔액조회
        return self.balance
    def save(self) : # 입출금 저장
        self.account[self.account_number] = self.balance

while True : 
    num = input("통장 번호를 입력해주세요.\n>>>")
    myBank = Bank(num)

    if myBank.if_account() :
        break
    else :
        print("통장 번호가 일치하지 않습니다.")

while True :
    print()
    message = input("무엇을 도와드릴까요? 입금(1), 출금(2), 잔액조회(3), 종료(4)\n>>>")

    if message == "입금" or message == "1" :
        amount = input("얼마를 입금하시겠습니까?\n>>>")
        try :
            amount = int(amount)
        except :
            print("잘못된 값을 입력하셨습니다.")
        else :
            if amount <= 0 :
                print("0보다 작은 값은 입금할 수 없습니다.")
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
                print("0보다 작은 값은 출금할 수 없습니다.")
            elif amount > myBank.balance :
                print(f"잔액보다 큰 값은 출금할 수 없습니다. 현재 잔액은 {myBank.balance}원입니다.")
            else :
                myBank.withdraw(int(amount))
    elif message == "잔액조회" or message == "3" :
        print(f"{num} 통장의 남은 잔액은 {myBank.get_balance()}원 입니다.")
    elif message == "종료" or message == "4" :
        print("이용해 주셔서 감사합니다.")
        break
    else :
        print("잘못된 값을 입력하셨습니다.")
