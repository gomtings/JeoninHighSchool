"""프로세스 감시 테스트.  실행:  pytest -v

테스트용으로 해롭지 않은 프로세스(ping / sleep)를 직접 띄운 뒤, 그것만 찾아서 종료하는지 확인한다.
"""
import subprocess
import sys
import time

import psutil
import pytest

from process_guard import PROTECTED, find_blacklisted, kill

LONG_COMMAND = (["ping", "-n", "60", "127.0.0.1"] if sys.platform == "win32" else ["sleep", "60"])


@pytest.fixture
def victim():
    """테스트 대상 프로세스를 띄우고, 테스트가 끝나면 반드시 정리한다."""
    proc = subprocess.Popen(LONG_COMMAND, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    yield proc, psutil.Process(proc.pid).name()
    if proc.poll() is None:
        proc.kill()
    proc.wait()


def test_차단_목록에_있는_프로세스를_찾는다(victim):
    proc, name = victim
    assert (proc.pid, name) in find_blacklisted([name])


def test_이름의_대소문자는_구분하지_않는다(victim):
    proc, name = victim
    assert proc.pid in [pid for pid, _ in find_blacklisted([name.upper()])]


def test_차단_목록에_없는_이름은_찾지_않는다(victim):
    assert find_blacklisted(["no-such-program.exe"]) == []


def test_보호_대상은_목록에_있어도_찾지_않는다():
    # 실제로 실행 중이어도 (파이썬 자신, 탐색기 등) 결과에 나오면 안 된다
    assert find_blacklisted(list(PROTECTED)) == []


def test_찾은_프로세스를_종료한다(victim):
    proc, name = victim
    assert kill(proc.pid) is True
    proc.wait(timeout=5)
    assert proc.poll() is not None
    assert proc.pid not in [pid for pid, _ in find_blacklisted([name])]


def test_이미_없는_프로세스를_종료해도_오류가_나지_않는다():
    assert kill(99999999) is False
