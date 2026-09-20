"""
BLE_processor.py
BLE 통신 멀티프로세싱 버전

구조:
  - 메인 프로세스 → BLE 프로세스: command_queue (추천 방향 전송)
  - BLE 프로세스 → 메인 프로세스: response_queue (Arduino 응답 수신)

사용법:
    ble = ble_processor()
    ble.start()
    ble.send("Front")        # 메인에서 방향 전송
    msg = ble.get_response() # Arduino 응답 수신 (없으면 None)
    ble.stop()
"""

import asyncio
import multiprocessing
from multiprocessing import Process, Queue
from bleak import BleakScanner, BleakClient


# ── BLE 워커 함수 (독립 프로세스에서 실행) ────────────────────────
def _ble_worker(command_queue: Queue, response_queue: Queue,
                target_name: str, char_uuid: str):
    """
    별도 프로세스에서 실행.
    command_queue 에서 명령을 꺼내 Arduino로 전송.
    Arduino 응답은 response_queue 에 넣음.
    """
    recv_buffer = ""
    last_sent   = ""

    def notification_handler(sender, data):
        nonlocal recv_buffer, last_sent
        text = data.decode("utf-8", errors="ignore")
        recv_buffer += text

        while "\n" in recv_buffer:
            line, recv_buffer = recv_buffer.split("\n", 1)
            line = line.strip()
            if line and line != last_sent:
                print(f"[Arduino → PC]: {line}")
                try:
                    response_queue.put_nowait(line)
                except Exception:
                    pass

    async def send_loop(client):
        nonlocal last_sent
        while True:
            try:
                cmd = command_queue.get_nowait()
                if cmd == "__STOP__":
                    return "__STOP__"
                if client.is_connected:
                    last_sent = cmd
                    await client.write_gatt_char(
                        char_uuid, (cmd + "\n").encode("utf-8")
                    )
                    print(f"[PC → Arduino]: {cmd}")
                else:
                    print("[BLE] 연결 끊김 감지 -> 재연결 시도")
                    return "__RECONNECT__"
            except Exception:
                pass

            if not client.is_connected:
                print("[BLE] 연결 끊김 감지 -> 재연결 시도")
                return "__RECONNECT__"

            await asyncio.sleep(0.05)

    async def run():
        while True:
            try:
                # 종료 명령 여부 사전 확인
                try:
                    if not command_queue.empty():
                        check_cmd = command_queue.get_nowait()
                        if check_cmd == "__STOP__":
                            return
                        command_queue.put_nowait(check_cmd)
                except Exception:
                    pass

                print(f"[BLE] '{target_name}' 검색 중...")
                device = await BleakScanner.find_device_by_filter(
                    lambda d, ad: d.name == target_name, timeout=5.0
                )
                if not device:
                    print(f"[BLE] '{target_name}' 를 찾을 수 없습니다. (2초 후 자동 재시도)")
                    response_queue.put("__NOT_FOUND__")
                    await asyncio.sleep(2.0)
                    continue

                print(f"[BLE] 발견: {device.address} -> 연결 시도...")
                async with BleakClient(device) as client:
                    print(f"[BLE] ✅ 연결 성공: {client.is_connected}")
                    response_queue.put("__CONNECTED__")

                    await client.start_notify(char_uuid, notification_handler)
                    try:
                        res = await send_loop(client)
                        if res == "__STOP__":
                            return
                    except asyncio.CancelledError:
                        return
                    finally:
                        try:
                            await client.stop_notify(char_uuid)
                        except Exception:
                            pass
                print("[BLE] 연결 끊김 -> 2초 후 자동 재연결 루프 진입...")
                await asyncio.sleep(2.0)
            except Exception as e:
                print(f"[BLE] 통신/연결 오류 발생 ({e}) -> 2초 후 자동 재연결...")
                response_queue.put("__ERROR__")
                await asyncio.sleep(2.0)

    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        print("[BLE] 프로세스 종료")


# ── 메인 프로세스에서 사용하는 클래스 ────────────────────────────
class ble_processor:
    TARGET_NAME = "Nano_BLE"
    CHAR_UUID   = "abcdefab-1234-5678-1234-abcdefabcdef"

    def __init__(self):
        self._command_queue:  Queue = multiprocessing.Queue()
        self._response_queue: Queue = multiprocessing.Queue()
        self._process: Process = None

    def start(self):
        """BLE 프로세스 시작"""
        if self._process and self._process.is_alive():
            return
        self._process = Process(
            target = _ble_worker,
            args   = (
                self._command_queue,
                self._response_queue,
                self.TARGET_NAME,
                self.CHAR_UUID,
            ),
            daemon = True,
        )
        self._process.start()
        print("[BLE] 프로세스 시작")

    def stop(self):
        """BLE 프로세스 종료"""
        if self._process and self._process.is_alive():
            try:
                self._command_queue.put("__STOP__")
            except Exception:
                pass
            self._process.join(timeout=3.0)
            if self._process.is_alive():
                self._process.terminate()
        print("[BLE] 프로세스 종료")

    def send(self, message: str):
        """Arduino로 메시지 전송 (논블로킹). 최신 명령만 유지."""
        if self._process and self._process.is_alive():
            try:
                while not self._command_queue.empty():
                    try:
                        self._command_queue.get_nowait()
                    except Exception:
                        break
                self._command_queue.put_nowait(message)
            except Exception as e:
                print(f"[BLE] 전송 오류: {e}")

    def get_response(self):
        """Arduino 응답 수신 (없으면 None 반환, 논블로킹)."""
        try:
            return self._response_queue.get_nowait()
        except Exception:
            return None

    def is_alive(self) -> bool:
        return self._process is not None and self._process.is_alive()
