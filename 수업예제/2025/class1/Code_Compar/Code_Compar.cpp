#include <iostream>
#include <string>
class Student {
public:
    std::string name;
    int stu_num;
    Student(std::string name, int stu_num) {
        this->name = name;
        this->stu_num = stu_num;
    }
    void student_info_print() {
        std::cout << "제 이름은 : " << name << " 이고 학번은 : " << stu_num << " 입니다." << std::endl;
    }
};
int main() {
    std::string name;
    int stu_num;
    std::cout << "이름을 입력해 주세요: ";
    std::getline(std::cin, name);
    std::cout << "학번을 입력해 주세요: ";
    std::cin >> stu_num;
    Student stu(name, stu_num);
    stu.student_info_print();
    return 0;
}