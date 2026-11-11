"""프로세스 감시 예제: 차단 목록(블랙리스트)에 있는 프로그램이 실행 중인지 찾고, 원하면 종료한다.

노트북 에이전트의 '차단' 로직을 파이썬으로 검증하는 용도다. 실제 서비스 에이전트는 C#으로 이전한다.
**테스트 PC에서만 사용하고, 학생 노트북에 배포하지 않는다.**

기본은 '찾기만' 한다(dry-run). 종료는 --kill 을 줄 때만 한다.

실행 예:
    python process_guard.py --blacklist notepad.exe,game.exe            # 찾아서 목록만 출력
    python process_guard.py --blacklist notepad.exe --kill              # 찾아서 종료
    python process_guard.py --blacklist notepad.exe --kill --loop 2     # 2초마다 반복
"""
import argparse
import os
import time

import psutil

# 이 이름의 프로그램은 차단 목록에 있어도 절대 건드리지 않는다 (실수로 시스템을 망가뜨리지 않기 위한 안전장치)
PROTECTED = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "services.exe", "lsass.exe", "svchost.exe", "explorer.exe", "dwm.exe", "conhost.exe",
    "cmd.exe", "powershell.exe", "python.exe", "pythonw.exe", "py.exe",
}


def find_blacklisted(blacklist):
    """실행 중인 프로세스 중 차단 목록에 있는 것을 [(pid, 이름), ...] 로 돌려준다 (이름은 대소문자 무시)."""
    names = {n.strip().lower() for n in blacklist if n.strip()} - PROTECTED
    found = []
    for p in psutil.process_iter(["pid", "name"]):
        name = p.info["name"] or ""
        if name.lower() in names and p.info["pid"] != os.getpid():
            found.append((p.info["pid"], name))
    return found


def kill(pid, timeout=3.0):
    """정상 종료를 먼저 요청하고, 안 되면 강제 종료한다. 이미 없어졌으면 False."""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout)
        except psutil.TimeoutExpired:
            proc.kill()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def main():
    ap = argparse.ArgumentParser(description="차단 목록 프로세스 감시")
    ap.add_argument("--blacklist", required=True, help="차단할 프로그램 이름 (쉼표로 구분, 예: notepad.exe,game.exe)")
    ap.add_argument("--kill", action="store_true", help="찾은 프로세스를 종료한다 (없으면 목록만 출력)")
    ap.add_argument("--loop", type=float, default=0, help="이 간격(초)으로 반복한다 (0이면 한 번만)")
    args = ap.parse_args()
    blacklist = args.blacklist.split(",")

    ignored = [n for n in blacklist if n.strip().lower() in PROTECTED]
    if ignored:
        print(f"보호 대상이라 무시함: {', '.join(ignored)}")

    while True:
        for pid, name in find_blacklisted(blacklist):
            if args.kill:
                print(f"[종료] {name} (pid {pid}) -> {'성공' if kill(pid) else '실패'}", flush=True)
            else:
                print(f"[발견] {name} (pid {pid})  (종료하려면 --kill)", flush=True)
        if args.loop <= 0:
            break
        time.sleep(args.loop)


if __name__ == "__main__":
    main()
