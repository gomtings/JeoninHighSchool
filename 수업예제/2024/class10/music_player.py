#pip3 install playsound
#pip3 install pygame
import os
import pygame
import tkinter as tk
from tkinter import ttk ,Toplevel ,Text
from tkinter import messagebox
from tkinter.ttk import Button, Style
from datetime import datetime
from tkinter import filedialog

#root = tk.Tk()
#root.withdraw()
class music_player:
    def __init__(self):
        self.file_path = None
        self.music_btn = None
        self.path = "E:/GitHub/JeoninHighSchool/수업예제/class10/music_player"
        self.file = None
        self.error_flag = False
        self.new_window = None
        self.yes_file = False
        self.stopgo = False
        self.alarm_save = None
        try: 
            if not os.path.exists(self.path): # 번역 결과 저장을 위한 폴더 및 파일 생성..
                os.mkdir(self.path)
            if os.path.isfile(self.path+"/music.txt"): # 파일이 존재 하면?
                self.file = open(self.path+"/music.txt", 'r')# 파일 읽기....
                self.file_path = self.file.read()
                self.file.close()
                self.file = open(self.path+"/music.txt", 'w')# 파일을 새로 생성함..
                self.file.write(self.file_path)
                self.file.close()
                self.yes_file = True
            else:
                self.file = open(self.path+"/music.txt", 'w')
                self.file.close()
                self.yes_file = False
        except FileNotFoundError as e:
            self.error_flag = True
        except Exception as e:
            self.error_flag = True
        pygame.init()
        pygame.mixer.init()

    def Choice_file(self):
        self.file_path = filedialog.askopenfilename()
        file = self.file_path.split("/")
        self.music_btn.config(text=file[len(file)-1])
        self.file = open(self.path+"/music.txt", 'w')
        self.file.write(self.file_path)
        self.file.close()

    def player(self):
        pygame.mixer.music.load(player.file_path)
        pygame.mixer.music.play()
        pygame.time.Clock().tick(10)
    
    def stop(self):
        if not self.stopgo:
            pygame.mixer.music.pause()
            self.stopgo = True
        else:
            pygame.mixer.music.unpause()
            self.stopgo = False
    
    def on_close(self):
        self.new_window.destroy()
        self.new_window = None

    def Set_alarm(self):
        if self.new_window == None :
            self.new_window = Toplevel(root)
            self.new_window.geometry("380x90+800+200")
            self.new_window.protocol("WM_DELETE_WINDOW",self.on_close)
            # 날자 설정...
            Label2 =ttk.Label(self.new_window,text = "월") # 저작권 및 버전 표시.
            Label2.place(x=0,y=0)
            target = ttk.Combobox(self.new_window, width=10)
            target['values'] = ("1","2","3","4","5","6","7","8","9","10","11","12")
            target.grid(column=1, row=1)
            target.place(x=0,y=20)
            target.current(1)
            Label2 =ttk.Label(self.new_window,text = "일") # 저작권 및 버전 표시.
            Label2.place(x=100,y=0)            
            target = ttk.Combobox(self.new_window, width=10)
            target['values'] = ("1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20",
                                "21","22","23","24","25","26","27","28","30","31")
            target.grid(column=0, row=1)
            target.place(x=100,y=20)
            target.current(1)
            # 시간 설정... 
            Label2 =ttk.Label(self.new_window,text = "시") # 저작권 및 버전 표시.
            Label2.place(x=200,y=0)   
            target = ttk.Combobox(self.new_window, width=10)
            target['values'] = ("1","2","3","4","5","6","7","8","9","10","11","12")
            target.grid(column=1, row=1)
            target.place(x=200,y=20)
            target.current(1)
            Label2 =ttk.Label(self.new_window,text = "분") # 저작권 및 버전 표시.
            Label2.place(x=300,y=0)   
            target = ttk.Combobox(self.new_window, width=10)
            target['values'] = ("0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20",
                                "21","22","23","24","25","26","27","28","30","31","32","33","34","35","36","37","38","39","40",
                                "41","42","43","44","45","46","47","48","49","50","51","52","53","54","55","56","57","58","59")
            target.grid(column=0, row=1)
            target.place(x=300,y=20)
            target.current(1)
            # 알람 저장
            self.alarm_save = ttk.Button(self.new_window, text = "알람 저장",command=self.alarm_set)
            self.alarm_save.place(x=0, y=45, width=380, height=40)
    def alarm_set(self):
        pass
if __name__ == "__main__":    
    root = tk.Tk()
    player = music_player()
    root.title("music_player") # 윈도우 타이틀 지정 
    root.geometry("380x150+400+200") # 창크기 지정
    root.resizable(False,False)
    player.music_btn = ttk.Button(root, text = "음악선택",command=player.Choice_file)
    if player.yes_file:
        file = player.file_path.split("/")
        player.music_btn.config(text=file[len(file)-1])
    else:
        player.music_btn.config(text="음악선택")
    player.music_btn.place(x=0, y=5, width=380, height=40)
    player.music_btn = ttk.Button(root, text = "재생",command=player.player)
    player.music_btn.place(x=5, y=50, width=100, height=40)
    player.music_btn = ttk.Button(root, text = "일시 정지",command=player.stop)
    player.music_btn.place(x=110, y=50, width=100, height=40)
    player.music_btn = ttk.Button(root, text = "알람 설정",command=player.Set_alarm)
    player.music_btn.place(x=215, y=50, width=165, height=40)
    root.mainloop() #GUI 루프 실행.
