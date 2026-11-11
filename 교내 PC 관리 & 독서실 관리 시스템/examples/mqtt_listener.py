"""MQTT 수신기: Zigbee2MQTT 센서 메시지를 받아 좌석 상태머신에 넣고, 상태 변화를 출력한다.

실행 예 (Mosquitto 같은 MQTT 브로커가 먼저 떠 있어야 한다):
    python mqtt_listener.py --seats seat01,seat02          # 실제 시간 기준 (설정은 설계안 값)
    python mqtt_listener.py --seats seat01 --demo          # 데모용으로 시간 기준을 줄이고, 자동 예약/입실

다른 창에서 가짜 센서를 실행하면 상태 변화를 볼 수 있다:
    python fake_sensor.py demo --name seat01
"""
import argparse
import time

import paho.mqtt.client as mqtt

from seat_state_machine import Config, SeatMachine
from z2m_parser import TOPIC_PREFIX, parse_sensor_message

LOW_BATTERY = 20  # (%) 이하이면 경고

# 데모용: 분 단위 기준을 초 단위로 줄여서 짧은 시간에 모든 상태를 볼 수 있게 한다
DEMO_CONFIG = Config(reserve_timeout=60, away_timeout=30, return_confirm=3,
                     unauthorized_sit=10, report_grace=15)
DEMO_CODE = "4821"


def main():
    ap = argparse.ArgumentParser(description="Zigbee2MQTT 센서 -> 좌석 상태머신")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--seats", default="seat01", help="센서 friendly_name 목록 (쉼표로 구분)")
    ap.add_argument("--demo", action="store_true", help="시간 기준을 줄이고 자동으로 예약/입실한다")
    ap.add_argument("--seconds", type=float, default=0, help="이 시간(초)이 지나면 종료 (0이면 계속)")
    args = ap.parse_args()

    cfg = DEMO_CONFIG if args.demo else Config()
    seats = {name: SeatMachine(name, cfg) for name in args.seats.split(",")}
    printed = {name: 0 for name in seats}   # 이미 출력한 이벤트 수

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"브로커 연결: {reason_code}", flush=True)
        client.subscribe(f"{TOPIC_PREFIX}/+")      # 모든 센서의 상태 메시지

    def on_message(client, userdata, msg):
        info = parse_sensor_message(msg.topic, msg.payload)
        if info is None or info["name"] not in seats:
            return
        seat = seats[info["name"]]
        now = time.time()
        if info["battery"] is not None and info["battery"] <= LOW_BATTERY:
            print(f"[경고] {seat.seat_id} 배터리 {info['battery']}%", flush=True)
        if info["presence"] is not None:
            print(f"센서  {seat.seat_id}: presence={info['presence']}", flush=True)
            seat.on_presence(info["presence"], now)
            if args.demo and seat.state.value == "RESERVED" and info["presence"]:
                seat.check_in("demo", DEMO_CODE, DEMO_CODE, now)   # 데모: 착석하면 바로 입실

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.host, args.port)
    client.loop_start()                          # 수신은 별도 스레드가 맡는다

    start = time.time()
    if args.demo:
        for seat in seats.values():
            seat.reserve("demo", start)
    try:
        while args.seconds == 0 or time.time() - start < args.seconds:
            now = time.time()
            for name, seat in seats.items():
                seat.tick(now)                   # 시간 경과에 따른 전이 (1초마다)
                for ev in seat.events[printed[name]:]:
                    print(f"이벤트  {name}: {ev.name} {ev.detail}  -> 상태 {seat.state.value}", flush=True)
                printed[name] = len(seat.events)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
