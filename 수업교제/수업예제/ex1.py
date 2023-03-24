class student():
    name = ""
    stu_num = 0
    
    def __init__(self,name,stu_num):
        self.name = name
        self.stu_num = stu_num
    
    def student_info_print(self):
        print('제 이름은 : {} 이고 학번은 : {} 입니다.'.format(self.name,self.stu_num))
            
name = input("이름을 입력해 주세요.")
stu_num = int(input("학번을 입력해 주세요."))
stu = student(name,stu_num)
stu.student_info_print()

