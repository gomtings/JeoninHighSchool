from tkinter import *
import tkinter.ttk as ttk
import os
import sys
import urllib.request
import json

root = Tk() 
root.title("translate") 
root.geometry("640x480")

lst = ["한국어", "영어", "일본어", "태국어"]
li = ["ko", "en", "ja", "th"]

# 콤보 박스 프레임
frame_choose = Frame(root)
Label(frame_choose, text="source : ").pack(side="left")
txt = ttk.Combobox(frame_choose, height=5, values=lst, state="readonly")
txt.current(0)
txt.pack(side="left")
trst = ttk.Combobox(frame_choose, height=5, values=lst, state="readonly")
trst.current(1)
trst.pack(side="right")
Label(frame_choose, text="target : ").pack(side="right")
frame_choose.pack(side="top")

if not(len(lst) == len(li)):
    print("ERROR : 전달할 문자와, 반환할 문자의 개수가 같지 않습니다.")
    root.quit

def translate():
    source = txt.get()
    target = trst.get()
    for i in range(len(lst)):    
        if source == lst[i]:
            obj = li[i]
    for i in range(len(lst)):    
        if target == lst[i]:
            sbj = li[i]
    if sbj == obj:
        print("같은 것을 번역할 수 없습니다.")
        raise Exception()

    Message = entry.get()
    client_id = "HtRq75QBgv_Qw44yTZQQ" 
    client_secret = "Z7wU_x7szl" 
    encText = urllib.parse.quote(Message)
    data = "source={0}&target={1}&text=".format(obj, sbj) + encText
    url = "https://openapi.naver.com/v1/papago/n2mt" 
    request = urllib.request.Request(url) 
    request.add_header("X-Naver-Client-Id", client_id) 
    request.add_header("X-Naver-Client-Secret", client_secret) 
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode() 
    if rescode == 200:
        response_body = response.read()
        response_body = json.loads(response_body.decode('utf-8')) 
        response_body = response_body.get("message")
        response_body = response_body.get("result")
        After.config(text=response_body.get("translatedText"))
    else:
        print("Error Code:" + rescode)

# 입력 프레임 만들기.
frame_entry = Frame(root)
entry = Entry(frame_entry)
entry.pack(side="left", fill="x")
btn = Button(frame_entry, text="번역하기", command=translate)
btn.pack(side="bottom")
frame_entry.pack(side="top")

After = Label(root, text="번역 결과")
After.pack(side="top")

root.mainloop()