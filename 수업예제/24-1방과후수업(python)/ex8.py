"""
=================================================
* Project      :  DeepL API EX
* Description  : DeepL  API 를 활용한 번역기 앱
* Author       : Lee Sang Woo
* Date         : 2024-07-23
* Version      : 1.0 
===================* History *===================
*  2023-04-20 init 최초 생성...
"""
import requests
import json
Message = str(input("번역할 문자열을 입력해 주세요 : "))
url_for_deepl = 'https://api-free.deepl.com/v2/translate'
params = {'auth_key' : 'ba59a929-40d2-4d1b-99ed-170c538568d9:fx', 'text' : Message, 'source_lang' : 'KO', "target_lang": 'EN' }

result = requests.post(url_for_deepl, data=params, verify=True)
if result.status_code == 200:
    print("요청이 성공적으로 처리되었습니다.")
    response_body = result.json()
    text = response_body['translations'][0]['text'] # 번역 결과
    detected = response_body['translations'][0]['detected_source_language'] # 감지된 언어.
    print(f'번역할 언어({detected}) : {Message} -> 번역 결과 : {text} ')
else:
    print(f"요청 처리에 실패했습니다. 상태 코드: {result.status_code}")
    
#{'translations': [{'detected_source_language': 'KO', 'text': 'hello'}]}