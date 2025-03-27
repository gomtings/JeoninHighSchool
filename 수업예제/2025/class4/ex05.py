students = []

def add_student(name, age, grade):
    students.append({"name": name, "age": age, "grade": grade})

def find_student(name):
    for student in students:
        if student["name"] == name:
            return student
    return None

def print_all_students():
    for student in sorted(students, key=lambda x: x["name"]):
        print(f"이름: {student['name']}, 나이: {student['age']}, 학년: {student['grade']}")

while True:
    print("\n메뉴:")
    print("1. 학생 추가")
    print("2. 학생 검색")
    print("3. 모든 학생 출력")
    print("4. 종료")
    choice = input("작업을 선택하세요: ")

    if choice == "1":
        name = input("학생 이름: ")
        age = int(input("학생 나이: "))
        grade = input("학생 학년: ")
        add_student(name, age, grade)
        print(f"{name} 학생이 추가되었습니다.")
    elif choice == "2":
        name = input("검색할 학생 이름: ")
        student = find_student(name)
        if student:
            print(f"이름: {student['name']}, 나이: {student['age']}, 학년: {student['grade']}")
        else:
            print("해당 학생이 없습니다.")
    elif choice == "3":
        print("모든 학생 정보:")
        print_all_students()
    elif choice == "4":
        print("프로그램을 종료합니다.")
        break
    else:
        print("올바른 번호를 입력하세요.")
