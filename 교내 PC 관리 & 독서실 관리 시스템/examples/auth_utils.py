"""비밀번호 해시 (파이썬 표준 라이브러리만 사용).

비밀번호는 절대 그대로 저장하지 않는다. 해시(scrypt)로 바꿔서 저장하고, 로그인할 때 같은 방식으로 비교한다.
"""
import hashlib
import hmac
import os

_N, _R, _P = 2 ** 14, 8, 1   # scrypt 비용 설정 (값이 클수록 느리고 안전하다)


def hash_password(password, salt=None):
    """'scrypt$<salt>$<hash>' 형태의 문자열을 돌려준다. 같은 비밀번호도 salt 가 달라서 매번 결과가 다르다."""
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=_N, r=_R, p=_P)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    """저장된 해시와 입력한 비밀번호가 같은지 확인한다 (시간 차이로 정보를 흘리지 않도록 compare_digest 사용)."""
    try:
        scheme, salt_hex, digest_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=_N, r=_R, p=_P)
    except ValueError:
        return False
    return hmac.compare_digest(actual, expected)
