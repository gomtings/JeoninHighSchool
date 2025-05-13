import uuid
import threading
import time

class BankAccount:
    def __init__(self, owner, password):
        self.account_number = str(uuid.uuid4())[:8]  # 8자리 계좌 번호 생성
        self.owner = owner
        self.password = password  # 비밀번호 저장
        self.balance = 0.0
        self.transaction_history = []

    def verify_password(self, input_password):
        return self.password == input_password  # 비밀번호 검증

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transaction_history.append(f"입금: {amount}원 | 잔액: {self.balance}원")
            print(f"{amount}원이 입금되었습니다. 현재 잔액: {self.balance}원")
        else:
            print("올바른 금액을 입력하세요.")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append(f"출금: {amount}원 | 잔액: {self.balance}원")
            print(f"{amount}원이 출금되었습니다. 현재 잔액: {self.balance}원")
        else:
            print("출금 금액이 잔액보다 많거나 올바르지 않습니다.")

    def apply_interest(self, interest_rate):
        interest = self.balance * (interest_rate / 100)
        self.balance += interest
        self.transaction_history.append(f"이자 지급: {interest:.2f}원 | 잔액: {self.balance:.2f}원")

    def show_balance(self):
        print(f"{self.owner}님의 잔액: {self.balance:.2f}원")

    def show_transaction_history(self):
        print(f"\n{self.owner}님의 거래 내역:")
        for transaction in self.transaction_history:
            print(transaction)

class BankSystem:
    def __init__(self):
        self.accounts = {}  # 계좌번호를 키로 사용
        self.customers = {}  # 고객 이름을 키로 사용
        self.admin_password = "admin1234"  # 관리자 비밀번호
        self.interest_rate = 1.0  # 기본 이자율 (1%)
        self.start_interest_system()  # 자동 이자 시스템 실행

    def create_account(self):
        owner = input("사용자의 이름을 입력하세요: ")

        if owner in self.customers:
            print(f"{owner}님은 이미 계좌가 존재합니다! 계좌번호: {self.customers[owner].account_number}")
            return

        password = input("비밀번호를 설정하세요: ")
        account = BankAccount(owner, password)
        self.accounts[account.account_number] = account
        self.customers[owner] = account  # 고객 이름을 키로 계좌 저장
        print(f"계좌가 생성되었습니다! 계좌번호: {account.account_number}")

    def get_account(self):
        owner = input("계좌를 조회할 고객 이름을 입력하세요: ")
        account = self.customers.get(owner)
        if account:
            password = input("비밀번호를 입력하세요: ")
            if account.verify_password(password):
                return account
            else:
                print("비밀번호가 틀렸습니다.")
                return None
        else:
            print("해당 고객의 계좌를 찾을 수 없습니다.")
            return None

    def admin_login(self):
        password = input("관리자 비밀번호를 입력하세요: ")
        if password == self.admin_password:
            return True
        else:
            print("관리자 비밀번호가 틀렸습니다.")
            return False
    
    def show_all_accounts(self):
        if self.admin_login():
            total_customers = len(self.customers)
            print("\n=== 모든 고객 계좌 목록 ===")
            total_balance = 0

            # 잔액이 많은 순서로 정렬
            sorted_accounts = sorted(self.customers.items(), key=lambda x: x[1].balance, reverse=True)

            for owner, account in sorted_accounts:
                total_balance += account.balance
                print(f"이름: {owner}, 계좌번호: {account.account_number}, 잔액: {account.balance}원")

            print(f"\n총 고객 수: {total_customers}명 , 은행 전체 잔액: {total_balance}원")

    def delete_account(self):
        if self.admin_login():
            owner = input("삭제할 계좌의 고객 이름을 입력하세요: ")
            if owner in self.customers:
                del self.accounts[self.customers[owner].account_number]
                del self.customers[owner]
                print(f"{owner}님의 계좌가 삭제되었습니다.")
            else:
                print("해당 고객의 계좌를 찾을 수 없습니다.")
                        
    def set_interest_rate(self):
        if self.admin_login():
            try:
                new_rate = float(input("새로운 이자율(%)을 입력하세요: "))
                if new_rate >= 0:
                    self.interest_rate = new_rate
                    print(f"이자율이 {self.interest_rate}%로 변경되었습니다.")
                else:
                    print("이자율은 0 이상이어야 합니다.")
            except ValueError:
                print("올바른 숫자를 입력하세요.")

    def apply_interest_to_all(self):
        for account in self.customers.values():
            account.apply_interest(self.interest_rate)

    def start_interest_system(self):
        def interest_loop():
            while True:
                time.sleep(60)  # 1분마다 실행
                self.apply_interest_to_all()
                print("\n계좌에 이자가 지급되었습니다!\n")

        interest_thread = threading.Thread(target=interest_loop, daemon=True)
        interest_thread.start()

    def run(self):
        while True:
            print("\n=== 은행 시스템 메뉴 ===")
            print("1. 계좌 생성")
            print("2. 입금")
            print("3. 출금")
            print("4. 잔액 조회")
            print("5. 거래 내역 확인")
            print("6. 관리자 로그인")
            print("7. 종료")

            choice = input("원하는 기능을 선택하세요: ")

            if choice == "1":
                self.create_account()
            elif choice in ["2", "3", "4", "5"]:
                account = self.get_account()
                if account:
                    if choice == "2":
                        amount = int(input("입금할 금액을 입력하세요: "))
                        account.deposit(amount)
                    elif choice == "3":
                        amount = int(input("출금할 금액을 입력하세요: "))
                        account.withdraw(amount)
                    elif choice == "4":
                        account.show_balance()
                    elif choice == "5":
                        account.show_transaction_history()
            elif choice == "6":
                print("\n=== 관리자 기능 ===")
                print("1. 모든 계좌 조회")
                print("2. 계좌 삭제")
                print("3. 이자율 설정")

                admin_choice = input("원하는 기능을 선택하세요: ")
                if admin_choice == "1":
                    self.show_all_accounts()
                elif admin_choice == "2":
                    self.delete_account()
                elif admin_choice == "3":
                    self.set_interest_rate()
                else:
                    print("올바른 번호를 입력하세요.")
            elif choice == "7":
                print("은행 시스템을 종료합니다.")
                break
            else:
                print("올바른 번호를 입력하세요.")

# 시스템 실행
bank_system = BankSystem()
bank_system.run()
