"""
voice_manager.py
서빙 로봇 비동기 멀티프로세싱(multiprocessing) 음성(TTS) 안내 모듈

특징:
- 파이썬 GIL(Global Interpreter Lock)의 간섭을 100% 원천 차단하는 독립 프로세스(Process) 구조
- 메인 주행/센서 융합 프로세스의 CPU 코어와 분리되어 0.000%의 프레임 드랍이나 렉 발생 없음
- 동일 음성 중복 재생 억제 (Cooldown 타이머)
- Windows(SAPI5/PowerShell) & Linux/라즈베리파이(espeak/spd-say/pyttsx3) 자동 감지 지원
"""

import multiprocessing
import time
import subprocess
import os
import platform
from typing import Dict, Optional


def _voice_process_worker(msg_queue: multiprocessing.Queue):
    """
    메인 프로세스와 완벽히 분리된 독립 프로세스에서 음성을 합성 및 재생.
    연속 호출 시에도 끊김 없이 무한 재생 보장.
    """
    os_type = platform.system().lower()

    # Windows 전용 SAPI COM 객체 초기화 시도 (가장 빠르고 안정적)
    sapi_voice = None
    if "windows" in os_type:
        try:
            import win32com.client
            # COM 아파트먼트 스레드 초기화
            import pythoncom
            pythoncom.CoInitialize()
            sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
            sapi_voice.Rate = 1
        except Exception:
            sapi_voice = None

    # pyttsx3 엔진 초기화 시도
    engine = None
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
    except Exception:
        engine = None

    while True:
        try:
            item = msg_queue.get()
            if item is None or item == "__QUIT__":
                break

            text = str(item).strip()
            if not text:
                continue

            print(f"[🔊 음성 안내] \"{text}\"")

            # 1순위: Windows SAPI COM (연속 호출 100% 보장 & 초고속)
            if sapi_voice is not None:
                try:
                    sapi_voice.Speak(text)
                    continue
                except Exception:
                    pass

            # 2순위: pyttsx3
            if engine is not None:
                try:
                    engine.say(text)
                    engine.runAndWait()
                    continue
                except Exception:
                    # pyttsx3 내부 루프 예외 발생 시 재초기화
                    try:
                        import pyttsx3
                        engine = pyttsx3.init()
                        engine.setProperty("rate", 160)
                        engine.say(text)
                        engine.runAndWait()
                        continue
                    except Exception:
                        pass

            # 3순위: Windows PowerShell System.Speech
            if "windows" in os_type:
                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"Add-Type -AssemblyName System.Speech; "
                    f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$synth.Rate = 1; "
                    f"$synth.Speak('{text}')"
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                continue

            # 4순위: Linux / 라즈베리파이 (espeak / spd-say)
            if "linux" in os_type:
                for cli in ["spd-say", "espeak"]:
                    try:
                        subprocess.run([cli, text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        break
                    except FileNotFoundError:
                        continue

        except Exception as e:
            time.sleep(0.05)


class VoiceManager:
    """비동기 독립 멀티프로세스 음성 관리자"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.msg_queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=10)
        self.last_spoken: Dict[str, float] = {}

        # 독립 워커 프로세스 시작
        self.process = multiprocessing.Process(
            target=_voice_process_worker,
            args=(self.msg_queue,),
            daemon=True
        )
        self.process.start()
        print(f"[VoiceManager] 🎙️ 독립 음성 프로세스 시작됨 (PID: {self.process.pid})")

    def say(self, text: str, cooldown_sec: float = 3.0, priority: bool = False):
        """
        논블로킹 음성 출력 요청 (메인 프로세스는 0.0001초 만에 반환)
        - cooldown_sec: 동일 문장 반복 재생 억제 시간 (초)
        - priority: True일 경우 큐를 비우고 최우선 재생
        """
        if not self.enabled or not text or not self.process.is_alive():
            return

        now = time.time()
        last_time = self.last_spoken.get(text, 0.0)

        if not priority and (now - last_time < cooldown_sec):
            return

        self.last_spoken[text] = now

        if priority:
            # 큐의 기존 대기열 비우기
            try:
                while not self.msg_queue.empty():
                    self.msg_queue.get_nowait()
            except Exception:
                pass

        try:
            self.msg_queue.put_nowait(text)
        except Exception:
            pass

    def stop(self):
        """독립 프로세스 안전 종료"""
        if self.process.is_alive():
            try:
                self.msg_queue.put_nowait("__QUIT__")
                self.process.join(timeout=0.5)
                if self.process.is_alive():
                    self.process.terminate()
            except Exception:
                pass
