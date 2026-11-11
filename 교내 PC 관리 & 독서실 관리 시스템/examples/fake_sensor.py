"""가짜 센서: 실제 센서 없이 Zigbee2MQTT 센서 메시지를 MQTT 브로커에 올린다.

실행 예:
    python fake_sensor.py demo                       # 착석 -> 자리 비움 -> 지나가는 사람 -> 복귀
    python fake_sensor.py sit --name seat01          # 착석(presence: true) 한 번 전송
    python fake_sensor.py leave --name seat01        # 이탈(presence: false) 한 번 전송
    python fake_sensor.py demo --speed 4             # 4배 빠르게 재생

브로커 주소 기본값은 localhost:1883 이다 (--host, --port 로 바꾼다).
"""
import argparse
import json
import time

import paho.mqtt.client as mqtt

# (presence, 직전 대기 시간[초]) 목록. 이 순서대로 보낸다.
SCENARIOS = {
    "sit": [(True, 0)],
    "leave": [(False, 0)],
    "passerby": [(True, 0), (False, 2)],            # 지나가는 사람: 2초 만에 사라짐
    "demo": [
        (True, 0),     # 착석
        (False, 6),    # 자리를 비움
        (True, 5),     # 누군가 지나감 ...
        (False, 2),    # ... 2초 만에 사라짐 (복귀로 보면 안 된다)
        (True, 5),     # 학생이 돌아옴
        (True, 6),     # 계속 감지 (복귀 인정)
    ],
}


def build_payload(presence, battery=95, linkquality=120):
    """Zigbee2MQTT 가 올리는 것과 같은 모양의 JSON 문자열."""
    return json.dumps({"presence": presence, "battery": battery, "linkquality": linkquality})


def main():
    ap = argparse.ArgumentParser(description="가짜 센서 (Zigbee2MQTT 메시지 발행)")
    ap.add_argument("scenario", choices=sorted(SCENARIOS))
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--name", default="seat01", help="센서 friendly_name (주제의 마지막 부분)")
    ap.add_argument("--battery", type=int, default=95)
    ap.add_argument("--speed", type=float, default=1.0, help="재생 배속 (2 이면 두 배 빠르게)")
    args = ap.parse_args()

    # paho-mqtt 2.x 는 콜백 API 버전을 반드시 지정해야 한다
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port)
    client.loop_start()
    topic = f"zigbee2mqtt/{args.name}"
    try:
        for presence, wait in SCENARIOS[args.scenario]:
            time.sleep(wait / args.speed)
            info = client.publish(topic, build_payload(presence, args.battery))
            info.wait_for_publish()
            print(f"발행  {topic}  presence={presence}", flush=True)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
