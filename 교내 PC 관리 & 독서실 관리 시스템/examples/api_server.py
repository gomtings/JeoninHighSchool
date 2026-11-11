"""로그인 + 권한(학생/교사) + 좌석 API 예제 (FastAPI).

실행:   uvicorn api_server:app --reload        -> http://127.0.0.1:8000/docs (자동 문서에서 직접 눌러 볼 수 있다)

예제용 계정 (실제 서비스에서는 DB 에 두고 초기 비밀번호는 첫 로그인 때 바꾸게 한다):
    학생  s1001 / student-pw
    교사  t001  / teacher-pw     (교사 = 관리자)

설계안과의 대응
- 학생: 좌석 예약 (자기 학번으로만)
- 교사(관리자): 좌석 강제 퇴실 등 관리 기능
- 로그인하지 않으면 401, 권한이 없으면 403
"""
import secrets
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from auth_utils import hash_password, verify_password
from seat_state_machine import SeatMachine

DUMMY_HASH = hash_password("dummy")   # 없는 계정도 같은 시간이 걸리게 해서 계정 존재 여부를 숨긴다


class LoginBody(BaseModel):
    user_id: str
    password: str


def create_app(clock=time.time):
    app = FastAPI(title="독서실 API 예제")

    users = {
        "s1001": {"role": "student", "pw": hash_password("student-pw")},
        "t001": {"role": "teacher", "pw": hash_password("teacher-pw")},
    }
    tokens = {}                                                     # 토큰 -> {"user_id", "role"}
    seats = {f"seat{i:02d}": SeatMachine(f"seat{i:02d}") for i in range(1, 4)}
    app.state.seats = seats                                         # 테스트에서 센서 값을 넣을 때 사용

    def current_user(authorization: str = Header(default="")):
        scheme, _, token = authorization.partition(" ")
        user = tokens.get(token) if scheme.lower() == "bearer" else None
        if user is None:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")
        return user

    def teacher_only(user=Depends(current_user)):
        if user["role"] != "teacher":
            raise HTTPException(status_code=403, detail="교사(관리자)만 사용할 수 있습니다")
        return user

    def get_seat(seat_id):
        if seat_id not in seats:
            raise HTTPException(status_code=404, detail="없는 좌석입니다")
        return seats[seat_id]

    @app.post("/login")
    def login(body: LoginBody):
        user = users.get(body.user_id)
        ok = verify_password(body.password, user["pw"] if user else DUMMY_HASH)
        if user is None or not ok:
            raise HTTPException(status_code=401, detail="학번 또는 비밀번호가 올바르지 않습니다")
        token = secrets.token_urlsafe(32)
        tokens[token] = {"user_id": body.user_id, "role": user["role"]}
        return {"token": token, "role": user["role"]}

    @app.get("/seats")
    def list_seats(user=Depends(current_user)):
        return [{"seat": s.seat_id, "state": s.state.value, "student": s.student} for s in seats.values()]

    @app.post("/seats/{seat_id}/reserve")
    def reserve(seat_id: str, user=Depends(current_user)):
        if user["role"] != "student":
            raise HTTPException(status_code=403, detail="학생만 예약할 수 있습니다")
        if not get_seat(seat_id).reserve(user["user_id"], clock()):
            raise HTTPException(status_code=409, detail="이미 사용 중이거나 예약된 좌석입니다")
        return {"seat": seat_id, "state": seats[seat_id].state.value}

    @app.post("/seats/{seat_id}/force-checkout")
    def force_checkout(seat_id: str, user=Depends(teacher_only)):
        seat = get_seat(seat_id)
        seat.checkout(clock(), reason=f"teacher:{user['user_id']}")   # 누가 조치했는지 기록 (감사 로그의 시작)
        return {"seat": seat_id, "state": seat.state.value}

    return app


app = create_app()
