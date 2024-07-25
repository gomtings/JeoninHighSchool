"""
=================================================
* Project      :  파파고 번역기
* Description  : 파파고  API 를 활용한 번역기 앱
* Author       : Lee Sang Woo
* Date         : 2023-04-20
* Version      : 1.0 
===================* History *===================
*  2023-04-20 init 최초 생성...
*  2023-07-** 번역결과 저장 기능 추가...
"""
import os
import sys
import requests
import json
import tkinter as tk
from tkinter import ttk ,Toplevel ,Text
from tkinter import messagebox
from tkinter.ttk import Button, Style
from datetime import datetime
class Translator:
    def __init__(self):
        self.auth_key = "ba59a929-40d2-4d1b-99ed-170c538568d9:fx" # 개발자센터에서 발급받은 Client Secret 값
        self.srcLang = None
        self.tarLang = None
        self.translated = None
        self.source_len = ""
        self.target_len = ""
        self.Message = ""
        self.path = "C:/GitHub/JeoninHighSchool/수업예제/24-1방과후수업(python)/Papago_translator"
        self.file = None
        self.error_flag = False
        self.new_window = None
        
        try: 
            if not os.path.exists(self.path): # 번역 결과 저장을 위한 폴더 및 파일 생성..
                os.mkdir(self.path)
            self.file = open(self.path+"/translator_list.txt", 'a')
            self.file.close()
        except FileNotFoundError as e:
            messagebox.showinfo("!!!!!!","파일이 존재하지 않습니다."+str(e))
            self.error_flag = True
        except Exception as e:
            messagebox.showinfo("!!!!!!","오류가 발생하였습니다."+str(e))
            self.error_flag = True
    
    def Get_object(self,obj1,obj2,obj3):
        self.srcLang = obj1
        self.tarLang = obj2
        self.translated = obj3
        self.srcLang.insert(0, "None")
        self.tarLang.insert(0, "None")
        self.translated.insert(0, "DeepL 번역기를 시작합니다.")
    
    def translation(self,source_len,target_len,String):
        url = 'https://api-free.deepl.com/v2/translate'
        params = {'auth_key' : 'ba59a929-40d2-4d1b-99ed-170c538568d9:fx', 'text' : String, 'source_lang' : source_len, "target_lang": target_len}
        response = requests.post(url, data=params, verify=True)
        if response.status_code == 200:
            result = json.loads(response.text)
            self.parse(source_len,target_len,result)
        else:
            pass
    
    def on_close(self):
        self.new_window.destroy()
        self.new_window = None
    
    def road_list(self):
        if self.new_window == None :
            self.new_window = Toplevel(root)
            self.new_window.geometry("380x200+800+200")
            self.new_window.title("번역 결과")
            self.new_window.protocol("WM_DELETE_WINDOW",self.on_close)
            try:
                self.file = open(self.path+"/translator_list.txt", 'r')
                text = self.file.read()
                text_widget = Text(self.new_window)
                text_widget.insert('end', text)
                text_widget.pack()
                self.file.close()
            except Exception as e:
                messagebox.showinfo("!!!!!!","오류가 발생하였습니다."+str(e))
    
    def save_results(self,source_len,target_len,Message,srcLangType,tarLangType,translatedText):
        self.file = open(self.path+"/translator_list.txt", 'a')
        self.file.write("====="+self.get_date()+"=====\n")
        self.file.write(source_len+" -> "+target_len+"\n")
        self.file.write(Message+"\n")
        self.file.write("==========번역 결과==========\n")
        self.file.write(tarLangType+" -> "+srcLangType+"\n")
        self.file.write(translatedText+"\n\n")
        self.file.close()
    
    def parse(self,source,target,result = None):
        detected = result['translations'][0]['detected_source_language'] # 감지된 언어.
        text = result['translations'][0]['text'] # 번역 결과
        self.srcLang.delete(0,len(self.srcLang.get()))
        if source == '':
            self.srcLang.insert(0, detected)
        else:
            self.srcLang.insert(0, source)
        self.tarLang.delete(0,len(self.tarLang.get()))
        self.tarLang.insert(0, target)
        self.translated.delete(0,len(self.translated.get()))
        self.translated.insert(0, text)
        self.save_results(self.source_len,self.target_len,self.Message,source,target,text)
    
    def Choice(self):
        self.Message = input_text.get()
        if source.get() == "자동":
            self.source_len = ""
        elif source.get() == "한국어":
            self.source_len = "ko"
        elif source.get() == "영어":
            self.source_len = "en"
        elif source.get() == "일본어":
            self.source_len = "ja"
        elif source.get() == "중국어 간체":
            self.source_len = "zh-CN"
        elif source.get() == "중국어 번체":
            self.source_len = "zh-TW"
        elif source.get() == "베트남어":
            self.source_len = "vi"
        elif source.get() == "인도네시아어":
            self.source_len = "id"
        elif source.get() == "태국어":
            self.source_len = "th"            
        elif source.get() == "독일어":
            self.source_len = "de"
        elif source.get() == "러시아어":
            self.source_len = "ru"
        elif source.get() == "스페인어":
            self.source_len = "es"
        elif source.get() == "이탈리아어":
            self.source_len = "it"
        elif source.get() == "프랑스어":
            self.source_len = "fr"
        else:
            self.source_len = "error"
        #print(self.source_len)
        if target.get() == "한국어":
            self.target_len = "ko"
        elif target.get() == "영어":
            self.target_len = "en"
        elif target.get() == "일본어":
            self.target_len = "ja"
        elif target.get() == "중국어 간체":
            self.target_len = "zh-CN"
        elif target.get() == "중국어 번체":
            self.target_len = "zh-TW"
        elif target.get() == "베트남어":
            self.target_len = "vi"
        elif target.get() == "인도네시아어":
            self.target_len = "id"
        elif target.get() == "태국어":
            self.target_len = "th"            
        elif target.get() == "독일어":
            self.target_len = "de"
        elif target.get() == "러시아어":
            self.target_len = "ru"
        elif target.get() == "스페인어":
            self.target_len = "es"
        elif target.get() == "이탈리아어":
            self.target_len = "it"
        elif target.get() == "프랑스어":
            self.target_len = "fr"
        else:
            self.target_len = "error"
        
        if (self.source_len !="" and self.target_len != "") or (self.source_len !="error" and self.target_len != "error"):
            if self.source_len != self.target_len:
                if self.Message !="" and self.Message !=None and self.Message !="여기에 번역할 문자열을 입력해 주세요.":
                    self.translation(self.source_len,self.target_len,self.Message)
                else:
                    messagebox.showinfo("Null String"," 번역할 문자열을 입력해 주세요!!")
            else:
                 messagebox.showinfo("Language error","source 언어 와 target 언어 를 다르게 설정해 주세요!")        
        else:
            messagebox.showinfo("!!!!!!","잘못된 언어 입력입니다.")          
    
    def get_date(self):
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_now
if __name__ == "__main__":    
    root = tk.Tk()
    style = Style()
    style.configure('TButton', background=root['bg'],borderwidth=0)
    Translator = Translator()
    root.title("language Translator") # 윈도우 타이틀 지정 
    root.geometry("380x200+400+200") # 창크기 지정
    root.resizable(False,False)
    #Label2 =ttk.Label(root,text = "language Translator ver 0.0.1 Dev by snag woo lee") # 저작권 및 버전 표시.
    #Label2.place(x=100,y=180)
    button = ttk.Button(root, text="language Translator ver 0.0.1 Dev by snag woo lee",command=Translator.road_list,style='TButton')
    button.place(x=95, y=180, width=290, height=25)
    txt =ttk.Label(root,text = "source : ")
    txt.place(x=0,y=2)
    
    source = ttk.Combobox(root, width=12)
    source['values'] = ("자동","한국어","영어","일본어","중국어 간체","중국어 번체","베트남어","인도네시아어","태국어","독일어","러시아어","스페인어","이탈리아어","프랑스어")
    source.grid(column=1, row=1)
    source.place(x=50,y=2)
    source.current(0)
    
    txt =ttk.Label(root,text = "target : ")
    txt.place(x=170,y=2)
    
    target = ttk.Combobox(root, width=12)
    target['values'] = ("한국어","영어","일본어","중국어 간체","중국어 번체","베트남어","인도네시아어","태국어","독일어","러시아어","스페인어","이탈리아어","프랑스어")
    target.grid(column=1, row=1)
    target.place(x=220,y=2)
    target.current(1)
    
    # 입력창..
    input_text = tk.Entry(root, width=52)
    input_text.grid(column=5, row=1000)
    input_text.place(x=0,y=30)
    input_text.insert(0, "여기에 번역할 문자열을 입력해 주세요.")
    # 번역하기 버튼..
    btn2 = ttk.Button(root, text = "번역하기",command=Translator.Choice)
    btn2.place(x=150, y=55, width=80, height=25)
    Label2 =ttk.Label(root,text = "===================번역 결과=========================")
    Label2.place(x=0,y=85)
    txt =ttk.Label(root,text = "srcLangType : ")
    txt.place(x=0,y=113)
    # 번역결과..
    srcLang = tk.Entry(root, width=6)
    srcLang.grid(column=5, row=1000)
    srcLang.place(x=85,y=113)
    txt =ttk.Label(root,text = "tarLangType : ")
    txt.place(x=170,y=113)
    # 번역결과..
    tarLang = tk.Entry(root, width=6)
    tarLang.grid(column=5, row=1000)
    tarLang.place(x=260,y=113)
    #translatedText
    Label2 =ttk.Label(root,text = "===================translatedText===================")
    Label2.place(x=0,y=140)
    # 번역결과..
    translatedText = tk.Entry(root, width=52)
    translatedText.grid(column=5, row=1000)
    translatedText.place(x=0,y=160)
    Translator.Get_object(srcLang,tarLang,translatedText)
    
root.mainloop() #GUI 루프 실행.
if not Translator.error_flag:
    Translator.file.close()
