"""Zigbee2MQTT 센서 메시지를 해석한다 (MQTT 브로커 없이도 테스트할 수 있는 순수 함수).

Zigbee2MQTT는 센서 값을 'zigbee2mqtt/<friendly_name>' 주제(topic)에 JSON으로 올린다.
ZG-204ZP는 Zigbee2MQTT에서 'ZG-204ZK'(제조사 HOBEIAN) 모델로 인식될 수 있다.

  topic   : zigbee2mqtt/seat01
  payload : {"presence": true, "battery": 95, "linkquality": 120}

  presence : true(사람 있음) / false(없음)   * false는 fading_time(기본 설정값) 뒤에 올라온다
  battery  : 0~100 (%)                        * 보고까지 최대 24시간 걸릴 수 있다

센서가 아닌 주제(zigbee2mqtt/bridge/..., zigbee2mqtt/<이름>/availability 등)는 None 을 돌려준다.
"""
import json

TOPIC_PREFIX = "zigbee2mqtt"


def parse_sensor_message(topic, payload, prefix=TOPIC_PREFIX):
    """센서 메시지면 {"name", "presence", "battery"} 를, 아니면 None 을 돌려준다.

    presence / battery 는 메시지에 없으면 None 이다 (배터리만 올라오는 메시지도 있다).
    """
    parts = topic.split("/")
    if len(parts) != 2 or parts[0] != prefix or parts[1] == "bridge":
        return None
    try:
        data = json.loads(payload)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None

    presence = data.get("presence")
    if not isinstance(presence, bool):
        presence = None
    battery = data.get("battery")
    if isinstance(battery, bool) or not isinstance(battery, (int, float)):
        battery = None

    if presence is None and battery is None:
        return None
    return {"name": parts[1], "presence": presence, "battery": battery}
