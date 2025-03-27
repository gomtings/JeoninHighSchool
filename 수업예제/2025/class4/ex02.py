shopping_list = []

while True:
    print("\n메뉴:")
    print("1. 아이템 추가")
    print("2. 아이템 삭제")
    print("3. 쇼핑 리스트 보기")
    print("4. 종료")
    choice = input("원하는 작업의 번호를 입력하세요: ")

    if choice == "1":
        item = input("추가할 아이템을 입력하세요: ")
        shopping_list.append(item)
        print(f"{item}이(가) 리스트에 추가되었습니다.")
    elif choice == "2":
        item = input("삭제할 아이템을 입력하세요: ")
        if item in shopping_list:
            shopping_list.remove(item)
            print(f"{item}이(가) 리스트에서 삭제되었습니다.")
        else:
            print("해당 아이템이 리스트에 없습니다.")
    elif choice == "3":
        print("현재 쇼핑 리스트:", shopping_list)
    elif choice == "4":
        print("프로그램을 종료합니다.")
        break
    else:
        print("올바른 번호를 입력하세요.")
