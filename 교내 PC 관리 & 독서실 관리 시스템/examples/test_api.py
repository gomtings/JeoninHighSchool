"""로그인/권한 API 테스트.  실행:  pytest -v

서버를 따로 띄우지 않고 TestClient 로 API 를 직접 호출한다.
"""
import pytest
from fastapi.testclient import TestClient

from api_server import create_app
from auth_utils import hash_password, verify_password


@pytest.fixture
def client():
    return TestClient(create_app(clock=lambda: 1000.0))


def login(client, user_id, password):
    r = client.post("/login", json={"user_id": user_id, "password": password})
    return r


def auth(client, user_id, password):
    return {"Authorization": f"Bearer {login(client, user_id, password).json()['token']}"}


# ---------------------------------------------------------------- 비밀번호 해시
def test_해시는_원문을_담지_않고_매번_다르다():
    a, b = hash_password("secret"), hash_password("secret")
    assert "secret" not in a and a != b
    assert verify_password("secret", a) and verify_password("secret", b)


@pytest.mark.parametrize("stored", ["", "garbage", "scrypt$zz$zz", "md5$aa$bb"])
def test_잘못된_해시는_거부한다(stored):
    assert verify_password("secret", stored) is False


def test_다른_비밀번호는_거부한다():
    assert verify_password("wrong", hash_password("secret")) is False


# ---------------------------------------------------------------- 로그인
def test_로그인_성공은_토큰과_역할을_돌려준다(client):
    r = login(client, "s1001", "student-pw")
    assert r.status_code == 200 and r.json()["role"] == "student" and r.json()["token"]


@pytest.mark.parametrize("user_id, password", [("s1001", "wrong"), ("nobody", "student-pw")])
def test_로그인_실패는_같은_메시지로_거부한다(client, user_id, password):
    r = login(client, user_id, password)
    assert r.status_code == 401
    assert r.json()["detail"] == "학번 또는 비밀번호가 올바르지 않습니다"   # 계정이 있는지 알려주지 않는다


def test_응답에_비밀번호_해시가_들어있지_않다(client):
    assert "scrypt" not in login(client, "s1001", "student-pw").text


# ---------------------------------------------------------------- 권한
def test_로그인하지_않으면_401(client):
    assert client.get("/seats").status_code == 401
    assert client.get("/seats", headers={"Authorization": "Bearer fake-token"}).status_code == 401


def test_학생은_예약할_수_있고_같은_좌석을_다시_예약하면_409(client):
    h = auth(client, "s1001", "student-pw")
    assert client.post("/seats/seat01/reserve", headers=h).json()["state"] == "RESERVED"
    assert client.post("/seats/seat01/reserve", headers=h).status_code == 409
    seats = {s["seat"]: s for s in client.get("/seats", headers=h).json()}
    assert seats["seat01"]["student"] == "s1001"          # 토큰의 학번으로만 예약된다


def test_학생은_강제_퇴실을_할_수_없다(client):
    h = auth(client, "s1001", "student-pw")
    client.post("/seats/seat01/reserve", headers=h)
    assert client.post("/seats/seat01/force-checkout", headers=h).status_code == 403


def test_교사는_강제_퇴실을_할_수_있고_기록이_남는다():
    app = create_app(clock=lambda: 1000.0)
    c = TestClient(app)
    s, t = auth(c, "s1001", "student-pw"), auth(c, "t001", "teacher-pw")
    c.post("/seats/seat01/reserve", headers=s)
    assert c.post("/seats/seat01/force-checkout", headers=t).json()["state"] == "EMPTY"
    assert app.state.seats["seat01"].events[-1].detail["reason"] == "teacher:t001"


def test_교사는_학생_전용_예약을_할_수_없다(client):
    h = auth(client, "t001", "teacher-pw")
    assert client.post("/seats/seat01/reserve", headers=h).status_code == 403


def test_없는_좌석은_404(client):
    h = auth(client, "t001", "teacher-pw")
    assert client.post("/seats/seat99/force-checkout", headers=h).status_code == 404
