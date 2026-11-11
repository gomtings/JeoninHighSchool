"""좌석 상태머신 예제 (센서 없이도 테스트할 수 있도록 '시간'을 밖에서 넣어 준다).

상태 흐름 (설계안 '좌석 생명주기'):
    EMPTY(빈 좌석) -> RESERVED(예약됨) -> OCCUPIED(사용 중) <-> AWAY(자리 비움) -> EMPTY(퇴실)

핵심 규칙
- 빈 좌석에서는 센서 신호를 무시한다. 단, 3분 이상 연속 감지되면 '미예약 무단 착석'으로 기록한다.
- 예약 후 15분 안에 (입구 인증코드 입력 + 센서 착석 감지)가 모두 되어야 입실이 완료된다.
- 자리를 비우면(센서 false) 자동 퇴실 카운트다운(기본 45분)이 시작된다.
- 복귀는 '연속 감지'가 return_confirm 초 이상일 때만 인정한다 (지나가는 사람의 짧은 감지는 무시).
- 자리 비움 상태에서 다른 학생이 신고하면 10분 유예 후 강제 퇴실(벌점)되고, 좌석은 신고자에게 넘어간다.

사용 예:
    seat = SeatMachine("seat01")
    seat.reserve("s1001", now=0)
    seat.on_presence(True, now=5)
    seat.check_in("s1001", "4821", "4821", now=10)   # -> (True, "ok")
"""
from dataclasses import dataclass, field
from enum import Enum


class State(str, Enum):
    EMPTY = "EMPTY"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"
    AWAY = "AWAY"


@dataclass
class Config:
    reserve_timeout: float = 15 * 60    # 예약 후 입실 제한 (넘으면 노쇼)
    away_timeout: float = 45 * 60       # 자리 비움 -> 자동 퇴실 카운트다운
    # 복귀 인정에 필요한 연속 감지 시간(초). 설계안에 '1530초'로 적혀 있어 15~30초로 추정한다.
    # 값이 확정되면 여기만 고치면 된다.
    return_confirm: float = 20.0
    unauthorized_sit: float = 3 * 60    # 빈 좌석 연속 감지 -> 미예약 무단 착석 판별
    report_grace: float = 10 * 60       # 빈자리 신고 유예


@dataclass
class Event:
    time: float
    name: str
    detail: dict = field(default_factory=dict)


class SeatMachine:
    def __init__(self, seat_id, config=None):
        self.seat_id = seat_id
        self.cfg = config or Config()
        self.state = State.EMPTY
        self.student = None
        self.events = []
        self.present = False            # 센서의 현재 값
        self._present_since = None      # 현재 값이 시작된 시각 (값이 바뀔 때만 갱신)
        self._reserved_at = None
        self._away_since = None
        self._report_by = None
        self._report_at = None
        self._unauth_flagged = False

    # ------------------------------------------------------------ 외부 입력
    def on_presence(self, present, now):
        """센서 메시지가 올 때마다 호출한다. 같은 값이 반복돼도 '시작 시각'은 바뀌지 않는다."""
        if self._present_since is None or present != self.present:
            self.present = present
            self._present_since = now
        self._evaluate(now)

    def tick(self, now):
        """주기적으로(예: 1초마다) 호출해 시간 경과에 따른 전이를 처리한다."""
        self._evaluate(now)

    def reserve(self, student, now):
        if self.state != State.EMPTY:
            return False
        self.state = State.RESERVED
        self.student = student
        self._reserved_at = now
        self._emit(now, "reserved", student=student)
        return True

    def check_in(self, student, entered_code, valid_code, now):
        """입구 전광판의 인증코드 + 센서 착석(true)이 모두 맞아야 입실이 완료된다."""
        if self.state != State.RESERVED or self.student != student:
            return False, "not_reserved"
        if entered_code != valid_code:
            return False, "wrong_code"
        if not self.present:
            return False, "not_seated"
        self.state = State.OCCUPIED
        self._emit(now, "checked_in", student=student)
        return True, "ok"

    def report_vacant(self, reporter, now):
        """빈자리 신고. 자리 비움(AWAY) 상태에서만 접수한다."""
        if self.state != State.AWAY or self._report_by is not None or reporter == self.student:
            return False
        self._report_by = reporter
        self._report_at = now
        self._emit(now, "report_received", reporter=reporter)
        return True

    def checkout(self, now, reason="manual"):
        self._emit(now, "checked_out", student=self.student, reason=reason)
        self._reset()

    # ------------------------------------------------------------ 내부 로직
    def _evaluate(self, now):
        c = self.cfg
        if self.state == State.EMPTY:
            if self.present and now - self._present_since >= c.unauthorized_sit:
                if not self._unauth_flagged:
                    self._unauth_flagged = True
                    self._emit(now, "unauthorized_sit")
            elif not self.present:
                self._unauth_flagged = False

        elif self.state == State.RESERVED:
            if now - self._reserved_at >= c.reserve_timeout:
                self._emit(now, "no_show", student=self.student)
                self._reset()

        elif self.state == State.OCCUPIED:
            if not self.present:
                self.state = State.AWAY
                self._away_since = now
                self._emit(now, "away_started")

        elif self.state == State.AWAY:
            if self._report_by and now - self._report_at >= c.report_grace:
                self._forced_checkout(now)
            elif self.present and now - self._present_since >= c.return_confirm:
                self.state = State.OCCUPIED
                self._away_since = None
                if self._report_by:
                    self._emit(now, "report_cancelled", reporter=self._report_by)
                    self._report_by = self._report_at = None
                self._emit(now, "returned")
            elif now - self._away_since >= c.away_timeout:
                self.checkout(now, reason="auto_checkout")

    def _forced_checkout(self, now):
        reporter, student = self._report_by, self.student
        self._emit(now, "forced_checkout", student=student)
        self._emit(now, "penalty", student=student, reason="seat_hoarding")
        self._reset()
        # 좌석은 신고자에게 인계된다 (신고자는 다시 인증코드로 입실해야 한다)
        self.reserve(reporter, now)
        self._emit(now, "seat_transferred", to=reporter)

    def _reset(self):
        self.state = State.EMPTY
        self.student = None
        self._reserved_at = self._away_since = None
        self._report_by = self._report_at = None
        self._unauth_flagged = False

    def _emit(self, now, name, **detail):
        self.events.append(Event(now, name, detail))

    def event_names(self):
        return [e.name for e in self.events]
