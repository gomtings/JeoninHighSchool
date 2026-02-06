import asyncio
from bleak import BleakScanner, BleakClient
# python -m venv venv
#venv\Scripts\activate
#deactivate
deg = {}
d_name = "Nano_BLE"

# 🔹 Arduino에서 쓰는 Characteristic UUID
CHAR_UUID = "abcdefab-1234-5678-1234-abcdefabcdef"

# 🔹 수신 버퍼 (중요!)
recv_buffer = ""

def notification_handler(sender, data):
    global recv_buffer

    # UTF-8 조각 누적
    text = data.decode("utf-8", errors="ignore")
    recv_buffer += text

    # 줄바꿈 기준으로 메시지 완성
    while "\n" in recv_buffer:
        line, recv_buffer = recv_buffer.split("\n", 1)  # 첫 줄만 분리
        if line.strip():
            print(f"\nArduino → PC: {line.strip()}")


async def send_loop(client):
    loop = asyncio.get_running_loop()

    while True:
        # input()은 blocking → executor 사용
        msg = await loop.run_in_executor(
            None,
            input,
            "PC → Arduino: "
        )

        if msg.strip():
            # 🔹 끝에 \n 추가 (Arduino 쪽에서 구분용)
            await client.write_gatt_char(
                CHAR_UUID,
                (msg + "\n").encode("utf-8")
            )


async def main():
    print("BLE 장치 스캔 중... (5초)")
    devices = await BleakScanner.discover(timeout=5.0)

    if not devices:
        print("발견된 BLE 장치 없음")
        return

    for d in devices:
        print(f"이름: {d.name}, 주소: {d.address}")
        if d.name:
            deg[d.name] = d.address

    address = deg.get(d_name)
    if address is None:
        print("검색결과가 없습니다")
        return

    print(f"{d_name} 발견 주소: {address}")
    print("BLE 연결 시도 중...")

    async with BleakClient(address) as client:
        if not client.is_connected:
            print("BLE 연결 실패")
            return

        print("BLE 연결 성공!")

        # 🔹 Arduino → PC 알림 구독
        await client.start_notify(CHAR_UUID, notification_handler)

        print("\n 실시간 텍스트 송수신 시작")
        print(" - Arduino → PC : 즉시 표시")
        print(" - PC → Arduino : 입력 후 전송")
        print(" (Ctrl + C 로 종료)\n")

        await send_loop(client)


asyncio.run(main())