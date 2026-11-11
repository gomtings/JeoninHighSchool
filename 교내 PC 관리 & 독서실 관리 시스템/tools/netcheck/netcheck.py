#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A안(교내망 직결) 접속 테스트 도구  -  표준 라이브러리만 사용 (Python 3.8+)

교무실 PC / 학생 노트북이 독서실 허브 PC에 교내망으로 접속할 수 있는지 확인한다.

  [허브 PC]            python netcheck.py server
  [교무실 PC/노트북]   python netcheck.py check --host <허브 IP>
  [장기 관찰]          python netcheck.py watch --host <허브 IP> --duration 86400
  [내 IP 확인]         python netcheck.py info

check 가 확인하는 항목 (모두 PASS 이면 A안 사용 가능):
  1. TCP 연결   지정한 포트로 접속되는가 (방화벽/네트워크 분리 확인)
  2. HTTP 왕복  /ping 을 여러 번 호출해 손실과 지연을 측정
  3. POST 전송  /echo 로 1KB, 64KB 데이터를 보내 그대로 돌아오는가
  4. 실시간 수신 /stream 을 일정 시간 유지해 끊김 없이 받아지는가 (교사 알림 방식)
  참고. ICMP ping (막혀 있어도 판정에는 영향 없음)
"""
import argparse
import csv
import http.server
import json
import platform
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

DEFAULT_PORTS = [8000, 8080]
MAX_AVG_MS = 100.0      # 합격 기준(제안): 평균 왕복 지연
MAX_STREAM_GAP = 2.5    # 합격 기준(제안): 실시간 수신 간격 최대(초). 서버는 1초마다 보낸다.
# 시스템 프록시를 쓰지 않고 직접 연결한다 (A안은 직결 확인이 목적이며, 학교망 프록시 설정에 영향받지 않게 한다)
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

try:  # 윈도우 콘솔에서 인코딩 오류로 멈추지 않게 한다
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_ports(text):
    return [int(p) for p in text.split(",") if p.strip()]


def local_ips():
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return sorted(ips)


def my_ip_toward(host):
    """host 로 나갈 때 쓰는 내 IP (실제 패킷은 보내지 않는다)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, 9))
        return s.getsockname()[0]
    except OSError:
        return "?"
    finally:
        s.close()


# ============================================================ 서버 (허브 PC)
class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *args):
        print(f"[{now()}] {self.client_address[0]:>15}  {self.command} {self.path}", flush=True)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path == "/ping":
            self._json({"ok": True, "server_time": time.time(), "port": self.server.server_address[1]})
        elif path == "/stream":
            sec = int(urllib.parse.parse_qs(query).get("sec", ["30"])[0])
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                for i in range(sec):
                    self.wfile.write(f"data: {i} {time.time():.3f}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(1)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
        else:
            self._json({"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/echo":
            return self._json({"ok": False, "error": "not found"}, 404)
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        self._json({"ok": True, "len": len(data)})


def run_server(args):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # 파일로 리다이렉트해도 즉시 기록
    except Exception:
        pass
    servers = []
    for p in args.ports:
        try:
            srv = http.server.ThreadingHTTPServer((args.bind, p), Handler)
        except OSError as e:
            print(f"[오류] 포트 {p} 를 열 수 없습니다: {e}")
            continue
        srv.daemon_threads = True
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
    if not servers:
        sys.exit(1)
    opened = ",".join(str(s.server_address[1]) for s in servers)
    print(f"[{now()}] 테스트 서버 시작  포트: {opened}  (종료: Ctrl+C)", flush=True)
    print("이 PC의 IP 주소 (교무실 PC에서 --host 로 입력):", flush=True)
    for ip in local_ips():
        print(f"    {ip}", flush=True)
    print("\n접속이 안 되면 이 PC의 방화벽에서 포트를 허용하세요 (관리자 명령 프롬프트, 확인만 하고 직접 실행):")
    print(f'    netsh advfirewall firewall add rule name="netcheck" dir=in action=allow protocol=TCP localport={opened}\n')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n종료합니다.")


# ============================================================ 클라이언트
def http_get(url, timeout=3.0):
    t0 = time.perf_counter()
    with OPENER.open(url, timeout=timeout) as r:
        body = r.read()
    return (time.perf_counter() - t0) * 1000.0, body


def tcp_connect(host, port, timeout=3.0):
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, (time.perf_counter() - t0) * 1000.0, ""
    except OSError as e:
        return False, 0.0, e.__class__.__name__


class Report:
    def __init__(self):
        self.items = []

    def add(self, no, name, status, detail):
        self.items.append({"no": no, "name": name, "status": status, "detail": detail})
        print(f"[{status:<4}] {no}. {name}: {detail}", flush=True)


def check(args):
    rep = Report()
    host = args.host
    print(f"[{now()}] 접속 테스트 시작  대상: {host}  포트: {args.ports}")
    print(f"    이 PC의 IP: {my_ip_toward(host)}   (같은 네트워크 대역인지 허브 IP와 앞 3자리를 비교하세요)\n")

    # 1. TCP 연결
    results = [(p,) + tcp_connect(host, p) for p in args.ports]
    ok_ports = [r[0] for r in results if r[1]]
    detail = "  ".join(f"{p}:{'OK(%.0fms)' % ms if ok else 'FAIL(' + err + ')'}" for p, ok, ms, err in results)
    rep.add(1, "TCP 연결", "PASS" if ok_ports else "FAIL", detail)
    if not ok_ports:
        print("\n허브 서버에 연결할 수 없습니다. 확인할 것:")
        print("  - 허브 PC에서 server 가 실행 중인지, IP 주소가 맞는지")
        print("  - 허브 PC 방화벽이 포트를 막고 있는지")
        print("  - 교무실과 독서실이 서로 다른 네트워크(VLAN)라서 막혀 있는지 -> 전산 담당에게 문의")
        return finish(rep, args)
    port = ok_ports[0]
    base = f"http://{host}:{port}"

    # 2. HTTP 왕복
    rtts, fails = [], 0
    for _ in range(args.count):
        try:
            ms, _body = http_get(base + "/ping")
            rtts.append(ms)
        except (urllib.error.URLError, OSError):
            fails += 1
        time.sleep(0.2)
    if rtts:
        avg = sum(rtts) / len(rtts)
        ok = fails == 0 and avg <= args.max_avg
        rep.add(2, "HTTP 왕복", "PASS" if ok else "FAIL",
                f"{args.count}회 중 손실 {fails}회, 지연 최소/평균/최대 = "
                f"{min(rtts):.0f}/{avg:.0f}/{max(rtts):.0f} ms (기준: 손실 0, 평균 {args.max_avg:.0f}ms 이하)")
    else:
        rep.add(2, "HTTP 왕복", "FAIL", "응답 없음")

    # 3. POST 전송
    sizes, bad = (1024, 64 * 1024), []
    for n in sizes:
        try:
            req = urllib.request.Request(base + "/echo", data=b"x" * n, method="POST")
            with OPENER.open(req, timeout=5) as r:
                if json.loads(r.read()).get("len") != n:
                    bad.append(f"{n}B 길이 불일치")
        except (urllib.error.URLError, OSError, ValueError) as e:
            bad.append(f"{n}B {e.__class__.__name__}")
    rep.add(3, "POST 전송", "FAIL" if bad else "PASS", ", ".join(bad) if bad else "1KB, 64KB 모두 정상")

    # 4. 실시간 수신 (교사 알림용 연결 유지)
    sec = args.stream_sec
    print(f"      ... 실시간 수신 {sec}초 측정 중")
    times, err = [], ""
    try:
        with OPENER.open(f"{base}/stream?sec={sec}", timeout=5) as r:
            while True:
                line = r.readline()
                if not line:
                    break
                if line.startswith(b"data:"):
                    times.append(time.perf_counter())
    except (urllib.error.URLError, OSError) as e:
        err = e.__class__.__name__
    gaps = [b - a for a, b in zip(times, times[1:])]
    max_gap = max(gaps) if gaps else 0.0
    ok = not err and len(times) >= sec and max_gap <= MAX_STREAM_GAP
    rep.add(4, "실시간 수신", "PASS" if ok else "FAIL",
            f"{len(times)}/{sec}건 수신, 최대 간격 {max_gap:.1f}초" + (f", 오류 {err}" if err else ""))

    # 참고. ICMP ping (판정에 영향 없음)
    flag = "-n" if platform.system() == "Windows" else "-c"
    try:
        rc = subprocess.run(["ping", flag, "2", host], capture_output=True, timeout=15).returncode
        rep.add("-", "ICMP ping (참고)", "INFO", "응답 있음" if rc == 0 else "응답 없음 (막혀 있어도 A안 판정에는 영향 없음)")
    except Exception as e:
        rep.add("-", "ICMP ping (참고)", "INFO", f"실행 불가 ({e.__class__.__name__})")
    return finish(rep, args)


def finish(rep, args):
    judged = [i for i in rep.items if i["status"] in ("PASS", "FAIL")]
    ok = bool(judged) and all(i["status"] == "PASS" for i in judged) and len(judged) >= 4
    print("\n" + "=" * 60)
    if ok:
        print("판정: A안 사용 가능 (항목 1~4 모두 PASS)")
    else:
        print("판정: A안 조치 필요  ->  전산 담당과 협의 후 재시험, 해결이 안 되면 B안(중계 서버) 검토")
    print("=" * 60)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump({"time": now(), "host": args.host, "ports": args.ports, "a_plan_ok": ok, "items": rep.items},
                      f, ensure_ascii=False, indent=2)
        print(f"결과 파일 저장: {args.report}")
    return 0 if ok else 1


def watch(args):
    """독서실 운영 시간 동안 일정 간격으로 접속을 확인해 끊긴 시간대를 기록한다."""
    url = f"http://{args.host}:{args.port}/ping"
    start = time.time()
    end = start + args.duration
    state, down_since, outages, total, success = None, None, [], 0, 0
    print(f"[{now()}] 장기 관찰 시작  대상: {url}  간격: {args.interval}초  기간: {args.duration}초  (종료: Ctrl+C)")
    f = open(args.csv, "w", newline="", encoding="utf-8-sig")
    w = csv.writer(f)
    w.writerow(["시각", "성공", "지연(ms)", "오류"])
    try:
        while time.time() < end:
            ts, ok, rtt, err = now(), True, "", ""
            try:
                ms, _ = http_get(url, timeout=3.0)
                rtt = f"{ms:.0f}"
            except (urllib.error.URLError, OSError) as e:
                ok, err = False, e.__class__.__name__
            total += 1
            success += ok
            w.writerow([ts, int(ok), rtt, err])
            f.flush()
            if ok != state:
                print(f"[{ts}] {'연결됨' if ok else '끊김 (' + err + ')'}", flush=True)
                if not ok:
                    down_since = ts
                elif down_since:
                    outages.append((down_since, ts))
                    down_since = None
                state = ok
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n중단합니다.")
    finally:
        f.close()
    if down_since:
        outages.append((down_since, now() + " (관찰 종료 시점까지 끊김)"))
    pct = 100.0 * success / total if total else 0.0
    print("\n" + "=" * 60)
    print(f"관찰 {total}회, 성공 {success}회 ({pct:.1f}%), 끊긴 구간 {len(outages)}건")
    for a, b in outages:
        print(f"    {a}  ~  {b}")
    print(f"기록 파일: {args.csv}")
    print("=" * 60)
    return 0 if not outages else 1


def info(_args):
    print("이 PC의 IP 주소:")
    for ip in local_ips():
        print(f"    {ip}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="A안(교내망 직결) 접속 테스트 도구")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("server", help="허브 PC에서 실행하는 테스트 서버")
    s.add_argument("--ports", type=parse_ports, default=DEFAULT_PORTS, help="열 포트 (쉼표 구분, 기본 8000,8080)")
    s.add_argument("--bind", default="0.0.0.0")
    s.set_defaults(func=lambda a: run_server(a))

    c = sub.add_parser("check", help="교무실 PC/노트북에서 접속 테스트")
    c.add_argument("--host", required=True, help="허브 PC IP 주소")
    c.add_argument("--ports", type=parse_ports, default=DEFAULT_PORTS)
    c.add_argument("--count", type=int, default=20, help="HTTP 왕복 횟수")
    c.add_argument("--stream-sec", type=int, default=30, help="실시간 수신 측정 시간(초)")
    c.add_argument("--max-avg", type=float, default=MAX_AVG_MS, help="합격 기준 평균 지연(ms)")
    c.add_argument("--report", help="결과를 JSON 파일로 저장")
    c.set_defaults(func=check)

    w = sub.add_parser("watch", help="장기 관찰 (와이파이/교내망 끊김 기록)")
    w.add_argument("--host", required=True)
    w.add_argument("--port", type=int, default=DEFAULT_PORTS[0])
    w.add_argument("--interval", type=float, default=10.0, help="확인 간격(초)")
    w.add_argument("--duration", type=float, default=86400.0, help="관찰 기간(초), 기본 24시간")
    w.add_argument("--csv", default="netcheck_watch.csv", help="기록 파일")
    w.set_defaults(func=watch)

    i = sub.add_parser("info", help="이 PC의 IP 주소 표시")
    i.set_defaults(func=info)

    args = ap.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
