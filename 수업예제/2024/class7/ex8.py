"""
=================================================
* Project      :  파파고  API EX
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
Message = str(input("번역할 문자열을 입력해 주세요 : "))
client_id = "" # 개발자센터에서 발급받은 Client ID 값
client_secret = "" # 개발자센터에서 발급받은 Client Secret 값
encText = urllib.parse.quote(Message)
data = "source=ko&target=en&text=" + encText
url = "https://openapi.naver.com/v1/papago/n2mt"
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    response_body = json.loads(response_body.decode('utf-8'))
    response_body = response_body.get("message")
    response_body = response_body.get("result")
    print("translatedText = {} , ".format(response_body.get("translatedText")))
else:
    print("Error Code:" + rescode)
