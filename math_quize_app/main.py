from tkinter import *
import tkinter as tk
import random
import update_db as db
import IDB.IDB  as idb
#import ttkthemes as ttk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import messagebox


#window = tk.Tk() 
window = ThemedTk(theme="elegance")
window.title("math~gaki")
window.geometry("360x360+600+200")
window.resizable(True,True)
#window.configure(bg="gray") ##49A
#window.attributes("-fullscreen", True)
window.bind("<F11>", lambda event: window.attributes("-fullscreen",  not window.attributes("-fullscreen")))
window.bind("<Escape>", lambda event: window.attributes("-fullscreen", False))
title = tk.Label(window, text="MATHGAKI", width= 30, height= 2,relief="groove",bg= "#21325E",fg= "white")
title.place(x = 78,y=80 )
photo = PhotoImage(file="green c.png")
photo2 = PhotoImage(file="red c.png")
mascot = PhotoImage(file="greent Tiger.png")
#junlim = PhotoImage(file="jun.png")
su = Label(window, image=photo,width=100,bg="#49A")
fa = Label(window, image=photo2,width=100,bg="#49A")
btn = tk.Button(window,text="시작",width=29,height=2,command=lambda:start.login_page())
btn.place(x = 78,y=115)
secret = tk.Button(window,text="d",width=10,height=1,command=lambda:start.developer_check())
#secret.place(x = 180,y= 320)
gt = Label(window,image=mascot)#bg="#006400"
gt.place(x = 0,y=265)
frame = Frame(window)



#jun = Label(window,image=junlim,bg="#006400")
#jun.place(x= 255,y = 265)
try:
    a= db.connect_to_database
    su.place(x = 2000,y=0)
except:
    fa.place(x = 2000,y=0)






class mathgaki():
    global window

    def __init__(self):    
        self.a = 0
        self.b = 0
        self.c = 0
        self.check = 0
        self.answer = 0
        self.end_statistics = 0
        self.correct = 0
        self.incorrcet =0
        self.this = []
        self.Duplicate = []
        self.big_dic = db.fetch_data()
        self.button_dic = {}
        self.multi_choice = None
        self.insert_db = [{'book_num': '01', 'question': 'Q1', 'c_answer': '답1', 'f_answer1': '답2', 'f_answer2': '답3', 'f_answer3': '답4'}]
        self.insert_db_student = [{'id': '김윤호','pw' : 30202,'시도한 횟수': 0 }]
        self.student_info = idb.fetch_data()
        self.check_command = []
        '''
        self.book_name = None
        self.question = None
        self.c_answer = None
        self.f_answer1 = None
        self.f_answer2 = None
        self.f_answer3 = None
        '''

    def warning(self):
        pass

    def quit(self,n):
        a = n
        self.__init__()
        return a.destroy()



    def question_selct_funtion(self,b_n):
        big_dic_len = len(self.big_dic[b_n])
        if self.multi_choice == None:
            self.multi_choice = random.sample(sorted(self.big_dic[b_n]),big_dic_len)   #원래5
            print(self.big_dic[b_n])
            print(self.multi_choice)
            self.next_question(b_n)
        else:
            self.next_question(b_n)


    def next_question(self,b_n):
        global big_dic
        global multi_choice
        global cotae
        global q
        location = [0,1,2,3]
        location2 = [0,1,2]
        multi_choice_len = len(self.multi_choice)
        print(multi_choice_len)
        if(len(self.Duplicate) == 4):
            self.Duplicate = []
        question_slect = random.randint(0,multi_choice_len-1)
        answer = random.randint(0,3)
        cur_question = self.big_dic[b_n][self.multi_choice[question_slect]]  #원래
        k = self.multi_choice[question_slect]
        
        self.Duplicate.append(self.multi_choice[question_slect])
        question_label.config(text=self.multi_choice[question_slect])
        cotae = cur_question["정답"]
        q = random.randint(0,3)
        location.remove(q)
        del self.multi_choice[question_slect]
        for i in range(3):
            r = random.randint(i+1,4)
            a = random.choice(location)
            b = random.choice(location2)
            btns[q].config(text = cur_question["정답"])
            self.button_dic.setdefault(q,cur_question["정답"])
            btns[a].config(text = cur_question["오답"][b])
            self.button_dic.setdefault(a,cur_question["오답"][b])
            if(location == []):
                pass
            else:
                location.remove(a)
                location2.remove(b)

                    
    def check_answer(self,idx,w,b_n,stu_name):
        global answer
        global check
        global end_statistics
        global correct
        global incorrcet
        #idx = idx.get(Text) 
        #idx = int(idx)
        #next_question()
        #print(idx)
        print(self.end_statistics)
        print(self.correct)
        print(self.incorrcet)
        if(self.button_dic[idx] == self.button_dic[q]):
            self.end_statistics += 1
            self.correct = self.correct +1
            print("정답")
            
            if(self.end_statistics == 4):
                #self.end_statistics = 0 
                self.result_page(self.correct,self.incorrcet,b_n,stu_name)
                #self.correct = 0
                #self.incorrcet = 0
                self.quit(new)
            else:
                w.after(1000,self.question_selct_funtion(b_n))
        else:
            self.end_statistics += 1
            print("틀렸다")
            self.incorrcet = self.incorrcet +1
            if(self.end_statistics == 4):
                #end_statistics = 0 
                self.result_page(self.correct,self.incorrcet,b_n,stu_name)
                #self.correct = 0
                #self.incorrcet = 0
                self.quit(new)             
                
            else:
                w.after(1000,self.question_selct_funtion(b_n)) 
    
    def new_window(self,name,stu_name):
        global question_label
        global btns
        global new
        global choice_book
        self.__init__()
        new = Toplevel()
        new.title(name) 
        new.geometry("900x600+450+200")
        new.resizable(True,True)
        #new.attributes("-fullscreen", True)
        new.bind("<F11>", lambda event: window.attributes("-fullscreen",  not window.attributes("-fullscreen")))
        
        question_label =  Label(new,width=50,height=2,text="test",font=("나눔바른펜", 20,"bold"), bg= "#21325E",fg= "white")
        question_label.pack(pady=30)
        btns = []
        choice_book = self.big_dic['2']
        b_n = '2'
        for i in range(4):
            print(i)
            btn = Button(new,text=f"{i}",width=60,height=2,font=("나눔바른펜", 15,"bold"),bg="#F0F0F0",command=lambda x = i: self.check_answer(x,new,b_n,stu_name))
            btn.pack()
            btns.append(btn)
        self.question_selct_funtion(b_n)
        tk.Button(new, text="뒤로가기", relief="groove", command= lambda: self.quit(new)).pack(side=BOTTOM)

    def result_page (self,y,n,b_n,stu_name):
        result = Toplevel()
        result.title("결과창")
        result.geometry("360x206+450+200")
        result.resizable(True,True)
        tk.Label(result, text="결과", width= 50, height= 2,relief="groove").pack() 
        tk.Label(result, text=f"맞춘문제:   {y}", width= 50, height= 2,relief="groove").pack()
        tk.Label(result, text=f"틀린문제:   {n}", width= 50, height= 2,relief="groove").pack()
        if(y >2):
            tk.Label(result, text="열심히 읽었네요", width= 50, height= 2,relief="groove").pack()
        else:
            tk.Label(result, text="열심히 읽고 오도록 해요", width= 50, height= 2,relief="groove").pack()
            self.ERROR_COUNT(b_n,stu_name)
            
        tk.Button(result, text="뒤로가기", relief="groove", command= lambda: self.quit(result)).pack(side=BOTTOM)

 
    def ERROR_COUNT(self,b_n,stu_name):#구현중
        self.student_ec = eval(self.student_info[stu_name]['error_count'])
        a = self.student_ec['ERROR_COUNT'][int(b_n)-1]
        self.student_ec['ERROR_COUNT'][int(b_n)-1] = a+1
        print(self.student_ec['ERROR_COUNT'][int(b_n)-1])
        print(self.student_ec['ERROR_COUNT'])
        ec = self.student_ec['ERROR_COUNT']
        sn = self.student_info[stu_name]['student_num']
        idb.edit_error_count(stu_name,sn,ec)

    def login_page(self):
        login = Toplevel()
        login.title("로그인 페이지")
        login.geometry("360x360+200+200")
        login.resizable(True,True)
        self.id = Entry(login)
        self.id.pack()
        self.pw_input = Entry(login)
        self.pw_input.pack()
        login_btn = tk.Button(login,text="로그인",command=lambda:self.login_check())
        login_btn.pack()
        

    def login_check(self):
        id = self.id.get()
        pw = self.pw_input.get()
        print(id,pw)
        if(id in self.student_info):
            if(pw == self.student_info[id]['student_num']):
                self.choice_page(id)
            else:
                messagebox.showerror('error',"잘못된 비밀번호")
        else:
            messagebox.showerror("error","아이디가 잘못되었습니다")
    def choice_page(self,stu_name):
        choice_page_window = Toplevel()
        choice_page_window.title("mathgaki") 
        choice_page_window.geometry("1300x600+450+200")
        choice_page_window.resizable(True,True)
        choice_page_window.attributes("-fullscreen", True)
        choice_page_window.configure(bg="#006400") ##778899

        choice_page_window.bind("<F11>", lambda event: window.attributes("-fullscreen",  not window.attributes("-fullscreen")))
        title = tk.Label(choice_page_window, text="어느 책을 선택하신 건가요?",font=120,bg= "#FFFFFF",fg= "black",width= 90, height= 4,relief="groove")
        title.pack()
        for i in range(1,11):
            tk.Button(choice_page_window,text=i,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i :start.new_window(x,stu_name)).place(x = 0,y = i*80)
            tk.Button(choice_page_window,text=i+10,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+10:start.new_window(x,stu_name)).place(x = 175,y = i*80)
            tk.Button(choice_page_window,text=i+20,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+20:start.new_window(x,stu_name)).place(x = 175*2,y = i*80)
            tk.Button(choice_page_window,text=i+30,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+30:start.new_window(x,stu_name)).place(x = 175*3,y = i*80)
            tk.Button(choice_page_window,text=i+40,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+40:start.new_window(x,stu_name)).place(x = 175*4,y = i*80)
            tk.Button(choice_page_window,text=i+50,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+50:start.new_window(x,stu_name)).place(x = 175*5,y = i*80)
            tk.Button(choice_page_window,text=i+60,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+60:start.new_window(x,stu_name)).place(x = 175*6,y = i*80)
            tk.Button(choice_page_window,text=i+70,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+70:start.new_window(x,stu_name)).place(x = 175*7,y = i*80)
        for i in range(1,9):
            tk.Button(choice_page_window,text=i+80,width= 15,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i +80 :start.new_window(x,stu_name)).place(x = 175*8,y = i*80)

    def secret_page(self):
        self.secret_window = Toplevel()
        self.secret_window.title("문제 추가")
        self.secret_window.geometry("600x400+400+100")
        self.secret_window.resizable(False, False)

        self.book_num_label = tk.Label(self.secret_window, text="추가할 문제의 책 번호:")
        self.book_num_label.pack(anchor=tk.W, padx=10, pady=10)
        self.book_num_entry = tk.Entry(self.secret_window)
        self.book_num_entry.pack(fill=tk.X, padx=10)
        
        self.problem_input_label = tk.Label(self.secret_window, text="문제입력:")
        self.problem_input_label.pack(anchor=tk.W, padx=10, pady=10)
        self.problem_input_entry = tk.Entry(self.secret_window)
        self.problem_input_entry.pack(fill=tk.X, padx=10)
        
        self.c_answer_label = tk.Label(self.secret_window, text="문제에 대한 정답 입력:")
        self.c_answer_label.pack(anchor=tk.W, padx=10, pady=10)
        self.c_answer_entry = tk.Entry(self.secret_window)
        self.c_answer_entry.pack(fill=tk.X, padx=10)

        self.f_answer1_label = tk.Label(self.secret_window, text="문제에 대한 오답1 입력:")
        self.f_answer1_label.pack(anchor=tk.W, padx=10, pady=10)
        self.f_answer1_entry = tk.Entry(self.secret_window)
        self.f_answer1_entry.pack(fill=tk.X, padx=10)

        self.f_answer2_label = tk.Label(self.secret_window, text="문제에 대한 오답2 입력:")
        self.f_answer2_label.pack(anchor=tk.W, padx=10, pady=10)
        self.f_answer2_entry = tk.Entry(self.secret_window)
        self.f_answer2_entry.pack(fill=tk.X, padx=10)

        self.f_answer3_label = tk.Label(self.secret_window, text="문제에 대한 오답3 입력:")
        self.f_answer3_label.pack(anchor=tk.W, padx=10, pady=10)
        self.f_answer3_entry = tk.Entry(self.secret_window)
        self.f_answer3_entry.pack(fill=tk.X, padx=10)


        
        add_button = tk.Button(self.secret_window, text="문제 추가", command=lambda:self.limjun_check('n'))
        add_button.pack(pady=10)
    
    def stu_info(self):
        self.info = Toplevel()
        self.info.title("학생정보")
        self.info.geometry("600x400+400+100")
        name = list(self.student_info.keys())
        tk.Label(self.info, text="찾을 학생의 이름입력").pack(anchor=tk.W, padx=10, pady=10)
        self.sn = tk.Entry(self.info)
        self.sn.pack(fill=tk.X, padx=10)    
        tk.Label(self.info, text="학생의 번호").pack(anchor=tk.W, padx=10, pady=10)
        self.sun = tk.Entry(self.info)
        self.sun.pack(anchor=tk.W, padx=10, pady=10)
        tk.Button(self.info, text="검색", command=lambda:self.search()).pack(pady=10)

    def search(self):
        dic ={}
        search_name = self.sn.get()
        stu_error = eval(self.student_info[search_name]['error_count'])
        self.sun.delete(0,'end')
        self.sun.insert(0,self.student_info[search_name]['student_num'])
        for i in range(len(stu_error['ERROR_COUNT'])):
            if(stu_error['ERROR_COUNT'][i]>0):
                dic[i+1] = stu_error['ERROR_COUNT'][i]
        for i in range(len(dic)):
            a = list(dic.keys())
            if(len(a)>0):
                tk.Label(self.info,text=f"{a[i]}권:{dic[a[i]]}").pack()
        if(len(dic)== 0):
            tk.Label(self.info,text="아직 문제를 풀지 않았어요").pack()
            
        

    def limjun_check(self,how):
        a = self.book_num_entry.get()
        b = self.problem_input_entry.get()
        c = self.c_answer_entry.get()
        d = self.f_answer1_entry.get()
        e = self.f_answer2_entry.get()       
        f = self.f_answer3_entry.get()
        if(a,b,c,d,e,f != ""):
            if(how == 'n'):
                print("통과")
                #self.going_limjun_db('n')
        else:
            messagebox.showerror("에러","공백입력 감지")
            self.book_num_entry.delete(0, tk.END)
            self.problem_input_entry.delete(0, tk.END)
            self.c_answer_entry.delete(0, tk.END)
            self.f_answer1_entry.delete(0, tk.END)
            self.f_answer2_entry.delete(0, tk.END)
            self.f_answer3_entry.delete(0, tk.END)
            

    def secret_page_view(self):
        view_window = Toplevel()
        view_window.title("문제들 목록확인")
        view_window.geometry("600x400+400+100")
        view_window.attributes("-fullscreen", True)
        view_window.bind("<Escape>", lambda event: view_window.attributes("-fullscreen", False))
        print(self.big_dic)
        for i in range(1,11):
            tk.Button(view_window,text=i,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i :self.view_page_deep(x)).place(x = 0,y = i*80)
            tk.Button(view_window,text=i+10,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+10:self.view_page_deep(x)).place(x = 175,y = i*80)
            tk.Button(view_window,text=i+20,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+20:self.view_page_deep(x)).place(x = 175*2,y = i*80)
            tk.Button(view_window,text=i+30,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+30:self.view_page_deep(x)).place(x = 175*3,y = i*80)
            tk.Button(view_window,text=i+40,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+40:self.view_page_deep(x)).place(x = 175*4,y = i*80)
            tk.Button(view_window,text=i+50,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+50:self.view_page_deep(x)).place(x = 175*5,y = i*80)
            tk.Button(view_window,text=i+60,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+60:self.view_page_deep(x)).place(x = 175*6,y = i*80)
            tk.Button(view_window,text=i+70,width= 18,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i+70:self.view_page_deep(x)).place(x = 175*7,y = i*80)
        for i in range(1,9):
            tk.Button(view_window,text=i+80,width= 15,height= 2, bg="#FFFFFF",font=(30),command= lambda x = i +80 :self.view_page_deep(x)).place(x = 175*8,y = i*80)
    
    def view_page_deep(self,n):
        deep_page = Toplevel()
        deep_page.title(n) 
        deep_page.geometry("1000x700+450+200")
        deep_page.resizable(True,True)
        n = str(n)  #딕셔너리의 키값이 문자열이다 따라서 n도 문자열로 바꾸어야 한다

        if(n in self.big_dic):
            question = list(self.big_dic[n].keys())
            for i in range(0,len(self.big_dic[n])):
                Label(deep_page,width=60,height=2,text=self.big_dic[n][question[i]],font=("나눔바른펜", 20,"bold"), bg= "#21325E",fg= "white").pack()

        else:
            Label(deep_page,width=50,height=2,text="문제가 없네요 추가해 주세요",font=("나눔바른펜", 20,"bold"), bg= "#21325E",fg= "white").pack()
                


    def clear(self,event,w):
        w.get()
        w.delete(0,len(w.get()))

    def going_limjun_db(self,how):
        if(how == 'n'):
            self.insert_db[0]['book_num'] = self.book_num_entry.get()
            self.insert_db[0]['question'] = self.problem_input_entry.get()
            self.insert_db[0]['c_answer'] = self.c_answer_entry.get()
            self.insert_db[0]['f_answer1'] = self.f_answer1_entry.get()
            self.insert_db[0]['f_answer2'] = self.f_answer2_entry.get()       
            self.insert_db[0]['f_answer3'] = self.f_answer3_entry.get()
            db.insert_data(self.insert_db)
            print("성공")
            print(self.insert_db)
            self.book_num_entry.delete(0, tk.END)
            self.problem_input_entry.delete(0, tk.END)
            self.c_answer_entry.delete(0, tk.END)
            self.f_answer1_entry.delete(0, tk.END)
            self.f_answer2_entry.delete(0, tk.END)
            self.f_answer3_entry.delete(0, tk.END)
            self.popup('n')

        elif(how == 'r'):
            if not(self.problem_input_entry.get() == ""):
                if(self.problem_input_entry.get() in self.big_dic):
                    db.delete_data_qn(self.problem_input_entry.get())
                    self.popup('r')
                else:
                    messagebox.showerror("에러","삭제할려는 문제가 없습니다")
            else:
                messagebox.showerror("에러","공백감지")
            
    def secret_choice(self):
        choice_modul_page = Toplevel()
        choice_modul_page.title("어떤 기능을 사용하시 겠어요?")
        choice_modul_page.geometry("360x360+200+200")
        btn1 = tk.Button(choice_modul_page,text="문제추가",command=lambda: self.secret_page()).pack()
        btn2 = tk.Button(choice_modul_page,text="문제제거",command=lambda: self.remove_q()).pack()
        btn3 = tk.Button(choice_modul_page,text="문제보기",command=lambda: self.secret_page_view()).pack()
        btn4 = tk.Button(choice_modul_page,text="학생정보 보기",command=lambda: self.stu_info()).pack()
    def remove_q(self):
        self.remove_page = Toplevel()
        self.remove_page.title("문제 삭제")
        self.remove_page.geometry("600x400+400+100")
        self.remove_page.resizable(False, False)
        problem_input_label = tk.Label(self.remove_page, text="삭제할 문제입력:")
        problem_input_label.pack(anchor=tk.W, padx=10, pady=10)
        self.problem_input_entry = tk.Entry(self.remove_page)
        self.problem_input_entry.pack(fill=tk.X, padx=10)
        add_button = tk.Button(self.remove_page, text="문제 삭제", command=lambda: self.going_limjun_db('r'))
        add_button.pack(pady=10)

    def popup(self,w):
        if(w == 'n'):
            messagebox.showinfo("성공","추가성공")
            self.quit(self.secret_window)
        elif(w == 'r'):
            messagebox.showinfo("성공","삭제성공")
            self.quit(self.remove_page)
    def password(self,window):
        password =  self.password_input.get()

        if(password == "632146s"):
            self.secret_choice()
            self.quit(window)
        else:
            self.None_password()
            self.quit(window)
    
    def None_password(self):
        messagebox.showerror("오류","잘못된 비밀번호입니다")

        

    def developer_check(self):
        devel_check_window = Toplevel()
        devel_check_window.title("password?")
        devel_check_window.geometry("360x360+200+200")
        devel_check_window.resizable(True,True)
        self.password_input = Entry(devel_check_window)
        self.password_input.pack()
        password_btn = tk.Button(devel_check_window,text="확인",command=lambda:self.password(devel_check_window))
        password_btn.pack()
    def kry_press(self,event):
        pass
        if(event == ["'6'","'3'","'2'","'1'","'4'","'6'","'s'"]):
            self.developer_check()
            

        else:
            print("올바르지 않은 커맨드")
            

#r = tk.Button(window,text="결과창미리보기",width= 15,height= 2, bg="gray",fg="yellow",font=(30),command= start.result_page)
#r.place(x = 175,y = 55)
c = []
def a(event):
    #c.append(int(repr(event.char)))
    c.append(repr(event.char))
    print(c) 
    if(repr(event.char) == "'s'"):
        start.kry_press(c)
        for i in range(len(c)):
            c.pop()
    else:
        pass

start = mathgaki()
window.bind("<Key>",a)
window.bind("<F1>", lambda event: start.developer_check())
window.mainloop()
     



















































'''
def next_question():
    global answer
    global cur_question
    global multi_choice
    global this
    location = [0,1,2,3]
    location2 = ["문제1","문제2","문제3","문제4"]
    qusetion = []
    multi_choice = random.sample(test_list,4)
    #multi_choice = random.sample(location2,3)
    print(multi_choice,"멀초")
    answer = random.randint(0,3) #4
    print(answer,"엔서")
    cur_question = multi_choice[answer][0]
    print(cur_question,"쿼 퀘스떤")
    question_label.config(text=cur_question)
    qusetion = multi_choice[answer]
    #r = random.randint(2,4)
    q = random.randint(0,3)
    location.remove(q)
    this.append(qusetion[1])
    for i in range(3):
        r = random.randint(i+1,4)
        a = random.choice(location)
        btns[q].config(text = qusetion[1]) #big_dic[1][cur_question]["정답"]
        btns[a].config(text = qusetion[a]) #big_dic[1][cur_question]["오답"][r]
        this.append(qusetion[r])
        if(location == []):
            pass
        else:
            location.remove(a)
        #btns[i].config(text = multi_choice[answer][i+1])
        #btns[i].config(lambda:check_answer(i,new))
        print(multi_choice[answer][i])
'''