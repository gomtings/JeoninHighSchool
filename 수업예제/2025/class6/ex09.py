class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"{amount}원이 입금되었습니다. 현재 잔액: {self.balance}원")

    def withdraw(self, amount):
        if amount > self.balance:
            print("잔액 부족!")
        else:
            self.balance -= amount
            print(f"{amount}원이 출금되었습니다. 현재 잔액: {self.balance}원")

# 테스트 코드
account = BankAccount("Sang", 10000)
account.deposit(5000)
account.withdraw(2000)
account.withdraw(15000)  # 잔액 부족 메시지 출력