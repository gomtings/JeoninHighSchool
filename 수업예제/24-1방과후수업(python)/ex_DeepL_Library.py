"""
=================================================
* Project      :  DeepL Library EX
* Description  : DeepL  Library 활용
* Author       : Lee Sang Woo
* Date         : 2024-07-25
* Version      : 1.0 
===================* History *===================
*  2023-04-20 init 최초 생성...
"""
import deepl
import json

Message = str(input("번역할 문자열을 입력해 주세요 : "))
auth_key = "ba59a929-40d2-4d1b-99ed-170c538568d9:fx"
translator = deepl.Translator(auth_key)
result = translator.translate_text(Message, source_lang="",target_lang="EN")
if result.status_code == 200:
    text = result.text # 번역 결과
    detected = result.detected_source_language # 감지된 언어.
    print(f'번역할 언어({detected}) : {Message} -> 번역 결과 : {text} ')
else:
    print(f"요청 처리에 실패했습니다. 상태 코드: {result.status_code}")

#{'translations': [{'detected_source_language': 'KO', 'text': 'hello'}]}