# 학생용 파이썬 예제 (좌석 상태머신 / MQTT / 로그인 API / 프로세스 감시)

센서나 실제 서버 없이도 개발과 테스트를 시작할 수 있도록 만든 예제입니다.
**실제 서비스 코드가 아니라 학습용 뼈대**입니다. 설계안의 규칙을 코드로 옮긴 예이므로, 값이 바뀌면 여기를 먼저 고치세요.

## 환경 준비

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -v                      # 전체 테스트 (49개)
```

- `requirements.txt`는 **ASCII 문자만** 써야 합니다. 한국어 윈도우의 `pip`은 이 파일을 cp949로 읽어서 한글 주석이 있으면 설치가 실패합니다.
- MQTT 예제(`mqtt_listener.py`, `fake_sensor.py`)를 실제로 돌리려면 **MQTT 브로커**가 필요합니다. 개발 PC에는 Mosquitto를 설치하면 됩니다(파이썬 패키지가 아니라 별도 프로그램). 브로커 없이는 아래 `pytest`만 가능합니다.

## 파일 구성

| 파일 | 내용 | 실행 방법 |
|---|---|---|
| `seat_state_machine.py` | 좌석 상태머신 (빈 좌석 → 예약 → 사용 중 ⇄ 자리 비움 → 퇴실, 노쇼, 빈자리 신고) | `test_seat_state_machine.py` 참고 |
| `test_seat_state_machine.py` | 상태머신 단위 테스트 13개 (시간을 직접 넣어서 검증) | `pytest -v` |
| `z2m_parser.py` | Zigbee2MQTT 센서 메시지 해석 | `test_z2m_parser.py` 참고 |
| `test_z2m_parser.py` | 파서 단위 테스트 14개 | `pytest -v` |
| `fake_sensor.py` | 가짜 센서: 센서 없이 MQTT 메시지 발행 | `python fake_sensor.py demo` |
| `mqtt_listener.py` | MQTT 수신 → 상태머신 → 상태 변화 출력 | `python mqtt_listener.py --seats seat01 --demo` |
| `auth_utils.py` | 비밀번호 해시(scrypt), 표준 라이브러리만 사용 | `test_api.py` 참고 |
| `api_server.py` | 로그인·권한(학생/교사)·좌석 API (FastAPI) | `uvicorn api_server:app --reload` 후 `/docs` |
| `test_api.py` | 해시·로그인·권한 테스트 16개 (서버를 띄우지 않고 호출) | `pytest -v` |
| `process_guard.py` | 차단 목록 프로세스 찾기/종료 (기본은 찾기만) | `python process_guard.py --blacklist notepad.exe` |
| `test_process_guard.py` | 프로세스 감시 테스트 6개 | `pytest -v` |

## MQTT 예제 따라 하기 (센서 없이)

1. MQTT 브로커를 실행합니다 (Mosquitto 등, 기본 포트 1883).
2. 창 1: `python mqtt_listener.py --seats seat01 --demo`
3. 창 2: `python fake_sensor.py demo --name seat01`
4. 창 1에서 `checked_in → away_started → returned` 순서로 상태가 바뀌는 것을 확인합니다.
   - 짧게 `true`가 왔다가 사라지는 구간(지나가는 사람)은 `returned`가 되지 않습니다.
   - 데모는 시간 기준을 분 단위에서 초 단위로 줄인 값입니다 (`mqtt_listener.py`의 `DEMO_CONFIG`).

실제 센서를 쓸 때는 Zigbee2MQTT가 `zigbee2mqtt/<friendly_name>` 주제에 `{"presence": true, "battery": 95, ...}` 형태로 올립니다. ZG-204ZP는 Zigbee2MQTT에서 `ZG-204ZK`(HOBEIAN) 모델로 인식될 수 있습니다.

## 센서 특성이 코드에 미치는 영향 (구매 전 확인한 자료 기준)

- `presence: false`는 센서의 `fading_time`(설정값, 최소 10초) 뒤에 올라옵니다. 상태머신의 시간 기준에는 이 지연이 포함됩니다.
- `battery`는 보고까지 **최대 24시간** 걸릴 수 있습니다. 처음 연결 직후에는 값이 없을 수 있으므로 코드에서 `None`을 처리해야 합니다 (`z2m_parser.py`가 그렇게 합니다).
- 센서 설정(`detection_distance`, `indicator` 등)은 반영에 **최대 10분**이 걸릴 수 있습니다.

## 알아둘 점

- 복귀 인정 시간(`Config.return_confirm`, 20초)은 설계안의 "1530초"를 15~30초로 추정한 **임시값**입니다. 확정되면 한 곳만 고치면 됩니다.
- `api_server.py`는 교육용입니다. 토큰 만료, 로그인 실패 잠금, HTTPS, DB 저장, 감사 로그가 **없습니다**. 실제 서비스에서는 반드시 추가해야 합니다 (설계안 "계정·권한 설계" 참고).
- `process_guard.py`는 **테스트 PC에서만** 쓰세요. 학생 노트북에 배포하지 않고, 서비스용 에이전트는 C#으로 이전합니다. 시스템 프로세스는 이름으로 보호되어 종료되지 않습니다.
- 모든 예제는 개발 PC에서 직접 실행해 검증했습니다 (전체 테스트 통과, 로컬 MQTT 브로커로 수신기와 가짜 센서 통신 확인, `uvicorn`으로 API 호출 확인). **실제 Zigbee2MQTT와 센서는 아직 연결해 보지 못했습니다.**
