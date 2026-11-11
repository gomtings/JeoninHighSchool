"""상태머신 단위 테스트.  실행:  pytest -v

센서도, 시계도 필요 없다. 'now' 값을 직접 넣어서 시간이 흐른 것처럼 만든다.
"""
import pytest

from seat_state_machine import Config, SeatMachine, State

MIN = 60


@pytest.fixture
def seat():
    return SeatMachine("seat01", Config())


def occupied_seat(seat, t=0):
    """예약 -> 착석 -> 입실 완료 상태로 만들어 준다."""
    seat.reserve("s1001", now=t)
    seat.on_presence(True, now=t + 5)
    ok, _ = seat.check_in("s1001", "4821", "4821", now=t + 10)
    assert ok
    return t + 10


# ---------------------------------------------------------------- 빈 좌석
def test_빈좌석에서_짧은_감지는_무시한다(seat):
    seat.on_presence(True, now=0)
    seat.tick(now=30)
    seat.on_presence(False, now=40)
    assert seat.state == State.EMPTY
    assert seat.events == []


def test_빈좌석에서_3분_연속_감지는_무단착석으로_기록한다(seat):
    seat.on_presence(True, now=0)
    seat.tick(now=3 * MIN)
    seat.tick(now=4 * MIN)                      # 여러 번 tick 해도
    assert seat.event_names() == ["unauthorized_sit"]   # 한 번만 기록


# ---------------------------------------------------------------- 예약과 입실
def test_예약후_15분_안에_입실하면_사용중이_된다(seat):
    occupied_seat(seat)
    assert seat.state == State.OCCUPIED


def test_예약후_15분_넘으면_노쇼로_취소된다(seat):
    seat.reserve("s1001", now=0)
    seat.tick(now=15 * MIN - 1)
    assert seat.state == State.RESERVED
    seat.tick(now=15 * MIN)
    assert seat.state == State.EMPTY
    assert "no_show" in seat.event_names()


@pytest.mark.parametrize("code, seated, expected", [
    ("0000", True, "wrong_code"),     # 코드가 틀림
    ("4821", False, "not_seated"),    # 코드는 맞지만 센서가 착석을 못 봄 (원격 입실 방지)
])
def test_입실_조건이_모두_맞아야_한다(seat, code, seated, expected):
    seat.reserve("s1001", now=0)
    seat.on_presence(seated, now=1)
    ok, reason = seat.check_in("s1001", code, "4821", now=2)
    assert (ok, reason) == (False, expected)
    assert seat.state == State.RESERVED


def test_다른_학생은_입실할_수_없다(seat):
    seat.reserve("s1001", now=0)
    seat.on_presence(True, now=1)
    assert seat.check_in("s1002", "4821", "4821", now=2) == (False, "not_reserved")


# ---------------------------------------------------------------- 자리 비움과 복귀
def test_자리를_비우면_카운트다운이_시작되고_45분_뒤_자동퇴실된다(seat):
    t = occupied_seat(seat)
    seat.on_presence(False, now=t + 1)
    assert seat.state == State.AWAY
    seat.tick(now=t + 1 + 45 * MIN - 1)
    assert seat.state == State.AWAY
    seat.tick(now=t + 1 + 45 * MIN)
    assert seat.state == State.EMPTY
    assert seat.events[-1].detail["reason"] == "auto_checkout"


def test_지나가는_사람의_짧은_감지는_복귀로_인정하지_않는다(seat):
    t = occupied_seat(seat)
    seat.on_presence(False, now=t + 1)           # 자리 비움
    seat.on_presence(True, now=t + 100)          # 누가 지나감
    seat.tick(now=t + 102)
    assert seat.state == State.AWAY              # 지나가는 중에도 복귀로 보지 않는다
    seat.on_presence(False, now=t + 103)         # 3초 만에 사라짐
    seat.tick(now=t + 200)
    assert seat.state == State.AWAY
    assert "returned" not in seat.event_names()


def test_연속_감지가_기준_시간을_넘으면_복귀로_인정하고_타이머를_리셋한다(seat):
    t = occupied_seat(seat)
    seat.on_presence(False, now=t + 1)
    seat.on_presence(True, now=t + 100)
    seat.on_presence(True, now=t + 110)          # 같은 값이 반복돼도 시작 시각은 유지
    seat.tick(now=t + 100 + seat.cfg.return_confirm)
    assert seat.state == State.OCCUPIED
    # 다시 자리를 비우면 새 카운트다운이 처음부터 시작된다
    seat.on_presence(False, now=t + 500)
    seat.tick(now=t + 500 + 44 * MIN)
    assert seat.state == State.AWAY


# ---------------------------------------------------------------- 빈자리 신고
def test_신고후_10분이_지나면_강제퇴실되고_좌석이_신고자에게_넘어간다(seat):
    t = occupied_seat(seat)
    seat.on_presence(False, now=t + 1)
    assert seat.report_vacant("s2002", now=t + 60)
    seat.tick(now=t + 60 + 10 * MIN - 1)
    assert seat.state == State.AWAY
    seat.tick(now=t + 60 + 10 * MIN)
    assert seat.state == State.RESERVED and seat.student == "s2002"
    names = seat.event_names()
    assert names[-4:] == ["forced_checkout", "penalty", "reserved", "seat_transferred"]


def test_신고후_복귀하면_신고가_취소된다(seat):
    t = occupied_seat(seat)
    seat.on_presence(False, now=t + 1)
    seat.report_vacant("s2002", now=t + 60)
    seat.on_presence(True, now=t + 120)
    seat.tick(now=t + 120 + seat.cfg.return_confirm)
    assert seat.state == State.OCCUPIED
    assert "report_cancelled" in seat.event_names()
    assert "penalty" not in seat.event_names()


def test_사용중인_좌석은_신고할_수_없다(seat):
    occupied_seat(seat)
    assert seat.report_vacant("s2002", now=100) is False
