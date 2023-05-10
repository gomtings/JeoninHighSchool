"""
=================================================
* Project      :  파파고 번역기
* Description  : 파파고  API 를 활용한 번역기 앱
* Author       : Lee Sang Woo
* Date         : 2023-04-20
* Version      : 1.0 
===================* History *===================
*  2023-04-20 init 최초 생성...
"""
import os
import sys
import urllib.request
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
class Translator:
    client_id = ""
    client_secret = ""
    source_len = ""
    target_len = ""
    Message = ""
    srcLang = None
    tarLang = None
    translated = None
    def __init__(self):
        self.client_id = "" # 개발자센터에서 발급받은 Client ID 값
        self.client_secret = "" # 개발자센터에서 발급받은 Client Secret 값
        self.srcLang = None
        self.tarLang = None
    def Get_object(self,obj1,obj2,obj3):
        self.srcLang = obj1
        self.tarLang = obj2
        self.translated = obj3
        self.srcLang.insert(0, "None")
        self.tarLang.insert(0, "None")
        self.translated.insert(0, "파파고 번역기를 시작합니다.")
    def translation(self,source_len,target_len,String):
        encText = urllib.parse.quote(String)
        data = "source={}&target={}&text=".format(source_len,target_len) + encText
        url = "https://openapi.naver.com/v1/papago/n2mt"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",self.client_id)
        request.add_header("X-Naver-Client-Secret",self.client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        
        if(rescode==200):
            response_body = response.read()
            self.parse(response_body.decode('utf-8'))
        else:
            self.parse()
            
    def parse(self,result =None):
        print(result)
        jsonObject = json.loads(result)
        jsonObject = jsonObject.get("message")
        jsonObject = jsonObject.get("result")
        self.srcLang.delete(0,len(self.srcLang.get()))
        self.srcLang.insert(0, jsonObject.get("srcLangType"))
        self.tarLang.delete(0,len(self.tarLang.get()))
        self.tarLang.insert(0, jsonObject.get("tarLangType"))
        self.translated.delete(0,len(self.translated.get()))
        self.translated.insert(0, jsonObject.get("translatedText"))
        
    def Choice(self):
        self.Message = input_text.get()
        if source.get() == "한국어":
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
        #print(self.target_len)
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
if __name__ == "__main__":    
    root = tk.Tk()
    Translator = Translator()
    root.title("language Translator") # 윈도우 타이틀 지정 
    root.geometry("380x215+400+200") # 창크기 지정
    root.resizable(False,False)
    Label2 =ttk.Label(root,text = "language Translator ver 0.0.1 Dev by snag woo lee") # 저작권 및 버전 표시.
    Label2.place(x=100,y=180)
    txt =ttk.Label(root,text = "source : ")
    txt.place(x=0,y=0)
    source = ttk.Combobox(root, width=12)
    source['values'] = ("한국어","영어","일본어","중국어 간체","중국어 번체","베트남어","인도네시아어","태국어","독일어","러시아어","스페인어","이탈리아어","프랑스어")
    source.grid(column=1, row=1)
    source.place(x=50,y=0)
    source.current(0)
    txt =ttk.Label(root,text = "target : ")
    txt.place(x=170,y=0)
    target = ttk.Combobox(root, width=12)
    target['values'] = ("한국어","영어","일본어","중국어 간체","중국어 번체","베트남어","인도네시아어","태국어","독일어","러시아어","스페인어","이탈리아어","프랑스어")
    target.grid(column=1, row=1)
    target.place(x=220,y=0)
    target.current(1)
    # 입력창..
    input_text = tk.Entry(root, width=52)
    input_text.grid(column=5, row=1000)
    input_text.place(x=0,y=30)
    input_text.insert(0, "여기에 번역할 문자열을 입력해 주세요.")
    # 번역하기 버튼..
    btn2 = ttk.Button(root, text = "번역하기",command=Translator.Choice);
    btn2.place(x=150, y=55, width=80, height=25)
    Label2 =ttk.Label(root,text = "===================번역 결과===================")
    Label2.place(x=0,y=85)
    txt =ttk.Label(root,text = "srcLangType : ")
    txt.place(x=0,y=110)
    # 번역결과..
    srcLang = tk.Entry(root, width=6)
    srcLang.grid(column=5, row=1000)
    srcLang.place(x=85,y=110)
    txt =ttk.Label(root,text = "tarLangType : ")
    txt.place(x=170,y=110)
    # 번역결과..
    tarLang = tk.Entry(root, width=6)
    tarLang.grid(column=5, row=1000)
    tarLang.place(x=260,y=110)
    #translatedText
    Label2 =ttk.Label(root,text = "===================translatedText===================")
    Label2.place(x=0,y=140)
    # 번역결과..
    translatedText = tk.Entry(root, width=52)
    translatedText.grid(column=5, row=1000)
    translatedText.place(x=0,y=160)
    Translator.Get_object(srcLang,tarLang,translatedText)
    
root.mainloop() #GUI 루프 실행.
