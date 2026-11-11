"""센서 메시지 해석 테스트.  실행:  pytest -v"""
import json

import pytest

from z2m_parser import parse_sensor_message


def test_정상_센서_메시지():
    payload = json.dumps({"presence": True, "battery": 95, "linkquality": 120})
    assert parse_sensor_message("zigbee2mqtt/seat01", payload) == {
        "name": "seat01", "presence": True, "battery": 95}


def test_bytes_payload도_처리한다():
    # paho-mqtt 는 payload 를 bytes 로 넘겨준다
    assert parse_sensor_message("zigbee2mqtt/seat02", b'{"presence": false}')["presence"] is False


def test_배터리만_있는_메시지():
    r = parse_sensor_message("zigbee2mqtt/seat01", '{"battery": 18}')
    assert r == {"name": "seat01", "presence": None, "battery": 18}


@pytest.mark.parametrize("topic", [
    "zigbee2mqtt/bridge/state",           # 브리지 상태
    "zigbee2mqtt/bridge",
    "zigbee2mqtt/seat01/availability",    # 센서 연결 상태
    "zigbee2mqtt/seat01/set",             # 설정 명령
    "other/seat01",                       # 다른 접두사
])
def test_센서가_아닌_주제는_무시한다(topic):
    assert parse_sensor_message(topic, '{"presence": true}') is None


@pytest.mark.parametrize("payload", [
    "not json", "", "[1, 2]", "null", '{"linkquality": 100}', '{"presence": "yes"}',
])
def test_해석할_수_없는_내용은_무시한다(payload):
    assert parse_sensor_message("zigbee2mqtt/seat01", payload) is None
