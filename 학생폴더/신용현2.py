# papago API

import urllib.request
import json
import tkinter as tk
from tkinter import ttk

def clear_entry(event):
    entry1.delete(0, tk.END)

def button_click() :
    message = entry1.get()
    lanType = {"한국어" : "ko", "영어" : "en", "일본어" : "ja"}
    encText = urllib.parse.quote(message)
    try : data = f"source={lanType[combo1.get()]}&target={lanType[combo2.get()]}&text=" + encText
    except KeyError :
        response_body = "에러가 발생했습니다 : 잘못된 언어"
        entry4.delete(0, tk.END)
        entry4.insert(0, response_body)
    else :
        url = "https://openapi.naver.com/v1/papago/n2mt"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        try : 
            response = urllib.request.urlopen(request, data=data.encode("utf-8"))
            rescode = response.getcode()
            if(rescode==200):
                response_body = response.read()
                response_body = json.loads(response_body.decode("utf-8")).get("message").get("result").get("translatedText")

                return f"translatedText = {response_body}"
            else:
                # print("Error Code:" + rescode)
                return "Error Code:" + rescode
        except :
            print("test")
            response_body = "에러가 발생했습니다 : 같은 언어로 번역할 수 없습니다."
            entry4.delete(0, tk.END)
            entry4.insert(0, response_body)   
        
        entry4.delete(0, tk.END)
        entry4.insert(0, response_body)
        entry2.delete(0, tk.END)
        entry3.delete(0, tk.END)
        entry2.insert(0, combo1.get())
        entry3.insert(0, combo2.get())
client_id = "HtRq75QBgv_Qw44yTZQQ"
client_secret = "Z7wU_x7szl"

root = tk.Tk()

label1 = tk.Label(root, text="source")
label1.grid(row=0,column=0)

combo1 = ttk.Combobox(root, values=["한국어", "영어", "일본어"])
combo1.current(0)
combo1.grid(row=0,column=1)

label1 = tk.Label(root, text="target")
label1.grid(row=0,column=2)

combo2 = ttk.Combobox(root, values=["영어", "한국어", "일본어"])
combo2.current(0)
combo2.grid(row=0,column=3)

entry1 = tk.Entry(root, width=50)
entry1.insert(0, "여기에 번역할 문자열을 입력해주세요")
entry1.bind("<FocusIn>", clear_entry)
entry1.grid(row=1, column=0, columnspan=3)

button1 = tk.Button(root, text="번역하기", width=20, command=button_click)
button1.grid(row=1,column=3)

label2 = tk.Label(root, text="============================번역 결과============================")
label2.grid(row=3,column=0, columnspan=4)

label3 = tk.Label(root, text="srcLangType")
label3.grid(row=4,column=0)

entry2 = tk.Entry(root)
entry2.insert(0, combo1.get())
entry2.grid(row=4, column=1)

label4 = tk.Label(root, text="tarLangType")
label4.grid(row=4,column=2)

entry3 = tk.Entry(root)
entry3.insert(0, combo2.get())
entry3.grid(row=4, column=3)

label5 = tk.Label(root, text="===========================translatedText===========================")
label5.grid(row=5,column=0, columnspan=4)

entry4 = tk.Entry(root, width=70)
entry4.insert(0, "파파고 번역기를 시작합니다.")
entry4.grid(row=6, column=0, columnspan=4)

root.mainloop()