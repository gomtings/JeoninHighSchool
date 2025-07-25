import uuid
import threading
import time
import random

class PropertyManager:
    def __init__(self):
        self.properties = []

    def add_property(self, real_estate):# 부동산 추가
        self.properties.append(real_estate)
        print(f"{real_estate.owner}님의 {real_estate.property_type}이(가) 추가되었습니다.")

    def remove_property(self, real_estate):
        """ 부동산 제거 """
        if real_estate in self.properties:
            self.properties.remove(real_estate)
            print(f"{real_estate.owner}님의 {real_estate.property_type}이(가) 삭제되었습니다.")
        else:
            print("해당 부동산을 찾을 수 없습니다.")

    def list_properties(self):# 등록된 부동산 목록 출력
        print("현재 관리 중인 부동산 목록:")
        for idx, prop in enumerate(self.properties, start=1):
            print(f"{idx}. {prop}")

    def buy_property(self,account, property): # 구매 기능
        name = account.owner
        budget = account.balance
        if property in self.properties:
            if budget >= property.price:
                budget -= property.price
                property.transfer_ownership(name)
                self.remove_property(property)  # 거래 완료 후 목록에서 삭제
                account.add_property(property) # 고객 재산 목록에 추가....
                print(f"{name}님이 {property.property_type}을(를) 구매했습니다!")
            else:
                print("예산이 부족합니다.")
        else:
            print("🚫 해당 매물이 존재하지 않습니다.")

    def sell_property(self,account,property, price): # 판매 기능
        if property in self.properties and property.owner == account.owner:
            property.price = price
            account.balance += price
            account.remove_property(property)
            #estate1 = Property(owners, area, price, type)
            #self.add_property(estate1)
            print(f"🛒 {account.owner}님이 {property.property_type}을(를) {price:,}₩에 판매 하였습니다.")
        else:
            print("부동산을 판매할 수 없습니다.")
    
    def simulate_transaction(self):
        """ 랜덤 부동산 거래 시뮬레이션 """
        if self.properties:
            property_to_sell = random.choice(self.properties)  # 랜덤 매물 선택
            
            # 랜덤 구매자 생성
            buyers = str(uuid.uuid4())[:8]
            # 랜덤 예산
            budget = random.randint(1000000, 200000000000)
            
            # 거래 금액을 면적 × 평당 가격으로 계산
            transaction_price = property_to_sell.area * property_to_sell.price
            
            if budget >= transaction_price :
                property_to_sell.transfer_ownership(buyers)
                self.remove_property(property_to_sell)  # 구매 후 목록에서 제거
            else:
                print(f"{buyers}님은 {property_to_sell.property_type}을 구매할 예산이 부족합니다.")
                            
class Property:
    def __init__(self, owner, area, price, property_type):
        self.owner = owner
        self.area = area  # 면적 (㎡)
        self.price = price  # 가격 (₩)
        self.property_type = property_type  # 유형 (아파트, 빌라 등)

    def __str__(self):
        return f"{self.owner}님의 {self.property_type} (면적: {self.area}㎡, 가격: {self.price:,}₩)"

    def update_price(self, new_price):
        """ 가격 변경 기능 """
        self.price = new_price
        print(f"{self.owner}님의 부동산 가격이 {new_price:,}₩으로 변경되었습니다.")

    def price_per_area(self):
        """ 면적당 가격 계산 """
        return self.price / self.area if self.area > 0 else 0

    def is_affordable(self, budget):
        """ 거래 가능 여부 확인 """
        return self.price <= budget

    def transfer_ownership(self, new_owner):
        """ 소유권 변경 """
        self.owner = new_owner
        print(f"부동산의 소유권이 {new_owner}님으로 변경되었습니다.")
        
class BankAccount:
    #모든 객체가 공유하는 변수
    total_accounts = 0  # 생성된 총 계좌 수
    strongbox = 100000  # 전체 은행 자금 (잔액 합계)
    exchange = 1000 #  환전은 기본 달러로만.

    def __init__(self, owner, password):
        self.account_number = str(uuid.uuid4())[:8]  # 8자리 계좌 번호 생성
        self.owner = owner
        self.password = password  # 비밀번호 저장
        self.balance = 0
        self.foreign_balance = 0
        self.loan = 0
        self.transaction_history = []
        self.Property = []
        
        BankAccount.total_accounts += 1

    def add_property(self, real_estate):# 부동산 추가
        self.Property.append(real_estate)
        print(f"{real_estate.owner}님의 {real_estate.property_type}이(가) 추가되었습니다.")
    
    def remove_property(self, real_estate):
        """ 부동산 제거 """
        if real_estate in self.properties:
            self.properties.remove(real_estate)
            print(f"{real_estate.owner}님의 {real_estate.property_type}이(가) 삭제되었습니다.")
        else:
            print("해당 부동산을 찾을 수 없습니다.")

    def list_properties(self):# 등록된 부동산 목록 출력
        print("현재 관리 중인 부동산 목록:")
        for idx, prop in enumerate(self.Property, start=1):
            print(f"{idx}. {prop}")
                                        
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
        total = self.loan + self.balance
        if 0 < amount <= total:
            self.balance -= amount
            self.transaction_history.append(f"출금: {amount}원 | 잔액: {total}원")
            print(f"{amount}원이 출금되었습니다. 현재 잔액: {total}원")
        else:
            print("출금 금액이 잔액보다 많거나 올바르지 않습니다.")

    def exchange_system(self, amount,type):
        if type == "WON":
            usd = amount / BankAccount.exchange
            if 0 < usd < self.balance:
                self.balance -= amount
                self.foreign_balance += amount
                self.transaction_history.append(f"한화 {amount}을 USD {usd}로 환전전되었습니다. 현재 잔액: {self.balance}원 이고 보유 달러는 {self.foreign_balance} 입니다.")
                print(f"한화 {amount}을 USD {usd}로 환전전되었습니다. 현재 잔액: {self.balance}원 이고 보유 달러는 {self.foreign_balance} 입니다.")
            else:
                print("환전 금액이이 올바르지 않습니다.")
        elif type == "USD":
            won = amount * BankAccount.exchange
            if 0 < amount < self.foreign_balance:
                self.balance += won
                self.foreign_balance -= amount
                self.transaction_history.append(f"usd {amount}을 won : {won}로 환전 되었습니다. 현재 잔액: {self.balance}원 이고 보유 달러는 {self.foreign_balance} 입니다.")
                print(f"usd {amount}을 won : {won}로 환전 되었습니다. 현재 잔액: {self.balance}원 이고 보유 달러는 {self.foreign_balance} 입니다.")
            else:
                print("환전 금액이이 올바르지 않습니다.")

    def account_transfer(self, amount,transfer):
        total = self.loan + self.balance
        if 0 < amount <= total:
            self.balance -= amount
            self.transaction_history.append(f"출금: {amount}원 | 잔액: {total}원")
            print(f"{amount}원이 이체 되었습니다. 현재 잔액: {total}원")
            transfer.deposit(amount)
        else:
            print("출금 금액이 잔액보다 많거나 올바르지 않습니다.")

    def Loans(self, loan):
        if 0 < loan and loan < BankAccount.strongbox and loan <= self.balance and loan <= self.loan:
            self.loan += loan
            BankAccount.strongbox -= loan
            self.transaction_history.append(f"대출: {loan}원 | 잔액: {self.loan}원")
            total = self.loan + self.balance
            print(f"{loan}원 을 대출이 승인 되었습니다. 현재 잔액: {total}원")
        else:
            print("대출이 불가능 합니다.")

    def Repayment(self, amount):
        if self.loan > 0:
            if amount > 0 and amount <= self.balance and amount <= self.loan:
                self.loan -= amount
                BankAccount.strongbox += amount
                self.transaction_history.append(f"상환: {amount}원 | 상환 후 잔액: {self.loan}원")
                print(f"{amount}원이 입금되었습니다. 현재 잔액: {self.balance}원")
            else:
                print("상환 할 금액을 다시 입력해 주세요!")
        else:
            print("상환 할 대출금이 존재하지 않습니다.")
                        
    def apply_interest(self, interest_rate):
        if self.balance > 0:
            interest = self.balance * (interest_rate / 100)
            self.balance += interest
            self.transaction_history.append(f"이자 지급: {interest:.2f}원 | 잔액: {self.balance:.2f}원")
            print("\n계좌에 이자가 지급되었습니다!\n")

    def apply_loan_interest(self, loan_rate):
        if self.loan > 0 and self.balance >0:
            interest = self.loan * (loan_rate / 100)
            self.balance -= interest
            BankAccount.strongbox += interest
            self.transaction_history.append(f"이자 출금: {interest:.2f}원 | 잔액: {self.balance:.2f}원")
        
    def show_balance(self):
        print(f"{self.owner}님의 잔액: {self.balance:.2f}원 / USD : {self.foreign_balance}")

    def show_transaction_history(self):
        print(f"\n{self.owner}님의 거래 내역:")
        for transaction in self.transaction_history:
            print(transaction)

class BankSystem:
    manager = PropertyManager()
    def __init__(self):
        self.accounts = {}  # 계좌번호를 키로 사용
        self.customers = {}  # 고객 이름을 키로 사용
        self.admin_password = "admin1234"  # 관리자 비밀번호
        self.interest_rate = 1.0  # 기본 이자율 (1%)
        self.loan_rate = 4.0  # 기본 이자율 (1%)
        self.start_interest_system(BankSystem.manager)  # 자동 이자 시스템 실행
        
    def create_account(self):
        owner = input("사용자의 이름을 입력하세요: ")

        if owner in self.customers:
            print(f"{owner}님은 이미 계좌가 존재합니다! 계좌번호: {self.customers[owner].account_number}")
            return

        password = input("비밀번호를 설정하세요: ")
        account = BankAccount(owner, password)
        self.accounts[account.account_number] = account
        self.customers[owner] = account  # 고객 이름을 키로 계좌 저장
        print(f"계좌가 생성되었습니다get_account! 계좌번호: {account.account_number}")

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

    def transfer_owner(self):
        owner = input("이체 할 고객 이름을 입력하세요: ")
        account = self.customers.get(owner)
        if account:
            return account
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

            print(f"\n총 고객 수: {total_customers}명 , 은행 예금 잔액: {total_balance}원 , 은행 금고 잔액: {BankAccount.strongbox}원")

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
            account.apply_loan_interest(self.loan_rate)

            
    def start_interest_system(self,PropertyManager):
        def interest_loop():
            manager = PropertyManager
            property_types = ["아파트", "빌라", "주택", "상가"]
            while True:
                time.sleep(60)  # 1분마다 실행
                # 이자 지급
                self.apply_interest_to_all()
                # 환율 조정
                BankAccount.exchange = random.uniform(1000, 2000)
                
                # 부동산 
                owners = str(uuid.uuid4())[:8]
                area = random.randint(20, 5000) # 평
                price = random.randint(100000, 30000000)  # 가격 랜덤 (10만원~3천)
                type = random.choice(property_types)
                estate1 = Property(owners, area, price, type)
                manager.add_property(estate1)
                
                # 부동산 거래 시뮬레이션
                manager.simulate_transaction()
            
        interest_thread = threading.Thread(target=interest_loop, daemon=True)
        interest_thread.start()

    def run(self):
        while True:
            print("\n=== 은행 시스템 메뉴 ===")
            print("1. 은행")
            print("2. 부동산")
            choice = input("원하는 기능을 선택하세요: ")
            
            if choice == "1":
                print("\n=== 은행 시스템 메뉴 ===")
                print("1. 계좌 생성")
                print("2. 입금")
                print("3. 출금")
                print("4. 잔액 조회")
                print("5. 거래 내역 확인")
                print("6. 대출")
                print("7. 상환")
                print("8. 계좌이체")
                print("9. 환전")
                print("10. 관리자 로그인")
                print("11. 종료")
                
                choice = input("원하는 기능을 선택하세요: ")
                if choice == "1":
                    self.create_account()
                elif choice in ["2", "3", "4", "5", "6", "7", "8", "9"]:
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
                            amount = int(input("대출할 금액을 입력하세요: "))
                            account.Loans(amount)
                        elif choice == "7":
                            amount = int(input("상환할 금액을 입력하세요: "))
                            account.Repayment(amount)
                        elif choice == "8": # 계좌 이체
                            transfer = self.transfer_owner()
                            if transfer:
                                amount = int(input("이체할 금액을 입력하세요: "))
                                account.account_transfer(amount,transfer)
                            else:
                                print("이체할 계좌가 존재하지 않습니다.")
                        elif choice == "9":
                            print("\n=== 환전소  ===")
                            print("1. Won -> USD")
                            print("2. USD -> Won")
                            choice = input("원하는 기능을 선택하세요: ")
                            if choice == "1":
                                amount = int(input("환전할 금액을 입력하세요(WON 로 입력): "))
                                account.exchange_system(amount,"WON")
                            elif choice == "2":
                                amount = float(input("환전할 금액을 입력하세요(USD 로 입력): "))
                                account.exchange_system(amount,"USD")
                elif choice == "10":
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
                elif choice == "11":
                    print("은행 시스템을 종료합니다.")
                    break
                else:
                    print("올바른 번호를 입력하세요.")
            elif choice == "2":
                print("\n=== 부동산 시스템 메뉴 ===")
                print("1. 매물 목록 출력")
                print("2. 부동산 구매")
                print("2. 부동산 판매")
                choice = input("원하는 기능을 선택하세요: ")
                if choice == "1":
                    BankSystem.manager.list_properties()
                elif choice == "2":
                    BankSystem.manager.list_properties()  # 현재 매물 목록 출력
                    property_index = int(input("\n구매할 부동산 번호를 입력하세요: ")) - 1

                    if 0 <= property_index < len(BankSystem.manager.properties):
                        account = self.get_account()
                        Property = BankSystem.manager.properties[property_index]
                        BankSystem.manager.buy_property(account, Property)
                    else:
                        print("올바른 번호를 입력하세요.")
                elif choice == "3":
                    account = self.get_account()
                    account.list_properties()  # 현재 매물 목록 출력
                    property_index = int(input("\n판매할 부동산 번호를 입력하세요: ")) - 1
                    if 0 <= property_index < len(BankSystem.manager.properties):
                        Property = BankSystem.manager.properties[property_index]
                        # 거래 금액을 면적 × 평당 가격으로 계산
                        transaction_price = Property.area * Property.price
                        price = int(input(f"판매 가격을 입력하세요 최초 구매 가격은 {transaction_price} 입니다. "))
                        BankSystem.manager.sell_property(account, transaction_price, price)
                else:
                    print("올바른 번호를 입력하세요.")
                
                
# 시스템 실행
bank_system = BankSystem()
bank_system.run()
