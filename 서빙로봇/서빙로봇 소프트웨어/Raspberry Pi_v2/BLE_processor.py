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
from console_utils import safe_print as _safe_print


# ── BLE 워커 함수 (독립 프로세스에서 실행) ────────────────────────
def _ble_worker(command_queue: Queue, response_queue: Queue,
                target_name: str, char_uuid: str, stop_event):
    """
    별도 프로세스에서 실행.
    command_queue 에서 명령을 꺼내 Arduino로 전송.
    Arduino 응답은 response_queue 에 넣음.
    종료 신호는 command_queue 가 아닌 별도의 stop_event 로 전달한다
    (같은 큐를 peek-and-requeue 하면 main 프로세스의 send() 드레인과
    경쟁해 명령 순서가 뒤바뀔 수 있기 때문).
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
                _safe_print(f"[Arduino → PC]: {line}")
                try:
                    response_queue.put_nowait(line)
                except Exception:
                    pass

    async def send_loop(client):
        nonlocal last_sent
        while True:
            if stop_event.is_set():
                return "__STOP__"
            try:
                cmd = command_queue.get_nowait()
                if client.is_connected:
                    last_sent = cmd
                    await client.write_gatt_char(
                        char_uuid, (cmd + "\n").encode("utf-8")
                    )
                    _safe_print(f"[PC → Arduino]: {cmd}")
                else:
                    _safe_print("[BLE] 연결 끊김 감지 -> 재연결 시도")
                    return "__RECONNECT__"
            except Exception:
                pass

            if not client.is_connected:
                _safe_print("[BLE] 연결 끊김 감지 -> 재연결 시도")
                return "__RECONNECT__"

            await asyncio.sleep(0.05)

    async def _run_with_stop_check(coro):
        """
        coro 실행 중 stop_event 가 설정되면 즉시 취소한다.
        (반환값: (중단됨 여부, 결과)) - 스캔/백오프 대기 중에도 stop() 요청에
        곧바로 반응하기 위함 (join(timeout=3.0) 초과로 강제 terminate 되는 것을 방지).
        """
        task = asyncio.ensure_future(coro)
        while not task.done():
            if stop_event.is_set():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                return True, None
            await asyncio.sleep(0.1)
        return False, task.result()

    async def run():
        while True:
            try:
                _safe_print(f"[BLE] '{target_name}' 검색 중...")
                stopped, device = await _run_with_stop_check(
                    BleakScanner.find_device_by_filter(
                        lambda d, ad: d.name == target_name, timeout=5.0
                    )
                )
                if stopped:
                    return
                if not device:
                    _safe_print(f"[BLE] '{target_name}' 를 찾을 수 없습니다. (2초 후 자동 재시도)")
                    response_queue.put("__NOT_FOUND__")
                    stopped, _ = await _run_with_stop_check(asyncio.sleep(2.0))
                    if stopped:
                        return
                    continue

                _safe_print(f"[BLE] 발견: {device.address} -> 연결 시도...")
                client = BleakClient(device)
                # connect() 자체도 오래 걸릴 수 있어 _run_with_stop_check 로 감싼다.
                # (그렇지 않으면 연결 시도 중 stop() 이 호출돼도 감지가 안 돼 강제 terminate 될 수 있음)
                stopped, _ = await _run_with_stop_check(client.connect())
                if stopped:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                    return

                try:
                    _safe_print(f"[BLE] ✅ 연결 성공: {client.is_connected}")
                    response_queue.put("__CONNECTED__")

                    stopped, _ = await _run_with_stop_check(
                        client.start_notify(char_uuid, notification_handler)
                    )
                    if stopped:
                        return

                    try:
                        res = await send_loop(client)
                        if res == "__STOP__":
                            return
                    finally:
                        try:
                            await client.stop_notify(char_uuid)
                        except Exception:
                            pass
                finally:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                _safe_print("[BLE] 연결 끊김 -> 2초 후 자동 재연결 루프 진입...")
                stopped, _ = await _run_with_stop_check(asyncio.sleep(2.0))
                if stopped:
                    return
            except Exception as e:
                _safe_print(f"[BLE] 통신/연결 오류 발생 ({e}) -> 2초 후 자동 재연결...")
                response_queue.put("__ERROR__")
                stopped, _ = await _run_with_stop_check(asyncio.sleep(2.0))
                if stopped:
                    return

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
        self._stop_event = multiprocessing.Event()
        self._process: Process = None

    def start(self):
        """BLE 프로세스 시작"""
        if self._process and self._process.is_alive():
            return
        self._stop_event.clear()
        self._process = Process(
            target = _ble_worker,
            args   = (
                self._command_queue,
                self._response_queue,
                self.TARGET_NAME,
                self.CHAR_UUID,
                self._stop_event,
            ),
            daemon = True,
        )
        self._process.start()
        _safe_print("[BLE] 프로세스 시작")

    def stop(self):
        """BLE 프로세스 종료"""
        if self._process and self._process.is_alive():
            self._stop_event.set()
            self._process.join(timeout=3.0)
            if self._process.is_alive():
                self._process.terminate()
        _safe_print("[BLE] 프로세스 종료")

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
                _safe_print(f"[BLE] 전송 오류: {e}")

    def get_response(self):
        """Arduino 응답 수신 (없으면 None 반환, 논블로킹)."""
        try:
            return self._response_queue.get_nowait()
        except Exception:
            return None

    def is_alive(self) -> bool:
        return self._process is not None and self._process.is_alive()
