accounts = {}

def create_account(account_number):
    if account_number in accounts:
        print("이미 존재하는 계좌입니다.")
    else:
        accounts[account_number] = 0
        print(f"{account_number} 계좌가 개설되었습니다.")

def deposit(account_number, amount):
    if account_number in accounts:
        accounts[account_number] += amount
        print(f"{amount}원이 입금되었습니다.")
    else:
        print("존재하지 않는 계좌입니다.")

def withdraw(account_number, amount):
    if account_number in accounts:
        if accounts[account_number] >= amount:
            accounts[account_number] -= amount
            print(f"{amount}원이 출금되었습니다.")
        else:
            print("잔액이 부족합니다.")
    else:
        print("존재하지 않는 계좌입니다.")

def check_balance(account_number):
    if account_number in accounts:
        print(f"{account_number} 계좌 잔액: {accounts[account_number]}원")
    else:
        print("존재하지 않는 계좌입니다.")

while True:
    print("\n메뉴:")
    print("1. 계좌 개설")
    print("2. 입금")
    print("3. 출금")
    print("4. 잔액 조회")
    print("5. 종료")
    choice = input("작업을 선택하세요: ")

    if choice == "1":
        account_number = input("계좌 번호를 입력하세요: ")
        create_account(account_number)
    elif choice == "2":
        account_number = input("입금할 계좌 번호를 입력하세요: ")
        amount = int(input("입금할 금액을 입력하세요: "))
        deposit(account_number, amount)
    elif choice == "3":
        account_number = input("출금할 계좌 번호를 입력하세요: ")
        amount = int(input("출금할 금액을 입력하세요: "))
        withdraw(account_number, amount)
    elif choice == "4":
        account_number = input("잔액을 조회할 계좌 번호를 입력하세요: ")
        check_balance(account_number)
    elif choice == "5":
        print("프로그램을 종료합니다.")
        break
    else:
        print("올바른 번호를 입력하세요.")
