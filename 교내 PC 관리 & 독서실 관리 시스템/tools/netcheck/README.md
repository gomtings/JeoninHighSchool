# netcheck - A안(교내망 직결) 접속 테스트 도구

교무실 PC와 학생 노트북이 독서실 허브 PC에 교내망으로 접속할 수 있는지 확인합니다.

| 파일 | 설명 | 필요한 것 |
|---|---|---|
| `netcheck.cmd` + `netcheck.ps1` | **PowerShell/CMD 버전 (권장)** | 윈도우 10/11 기본 PowerShell 5.1 (설치 없음) |
| `netcheck.py` | 파이썬 버전 | Python 3.8 이상 |

두 버전은 **같은 통신 규격**이라 섞어서 쓸 수 있습니다. 예: 허브 PC는 파이썬 `server`, 교무실 PC는 PowerShell `check`.
교무실 PC에는 파이썬이 없을 수 있으므로 PowerShell/CMD 버전을 기본으로 안내합니다.

## 실행 방법 (PowerShell/CMD 버전)

`netcheck.cmd`와 `netcheck.ps1` **두 파일을 같은 폴더에 복사**해서 사용합니다.

| 어디서 | 명령 (CMD) |
|---|---|
| 허브 PC (독서실) | `netcheck.cmd server` |
| 교무실 PC / 학생 노트북 | `netcheck.cmd check 192.168.0.10 -Report report.json` |
| 장기 관찰 (끊김 기록) | `netcheck.cmd watch 192.168.0.10 -Duration 86400` |
| 내 IP 확인 | `netcheck.cmd info` |

- PowerShell 창에서 실행할 때는 `.\netcheck.cmd check 192.168.0.10` 처럼 앞에 `.\`를 붙입니다.
- 옵션: `-Ports 8000,8080` `-Count 20` `-StreamSec 30` `-MaxAvg 100` (check), `-Port 8000` `-Interval 10` `-Duration 86400` `-Csv 파일명` (watch)
- `netcheck.cmd`는 `-ExecutionPolicy Bypass`로 `netcheck.ps1`을 실행하므로 스크립트 실행 정책을 바꿀 필요가 없습니다.

## 실행 방법 (파이썬 버전)

| 어디서 | 명령 |
|---|---|
| 허브 PC | `python netcheck.py server` |
| 교무실 PC / 노트북 | `python netcheck.py check --host <허브 IP> --report report.json` |
| 장기 관찰 | `python netcheck.py watch --host <허브 IP> --duration 86400` |

## 테스트 순서

1. 허브 PC에서 `server`를 실행하면 이 PC의 IP가 표시됩니다.
2. 접속이 안 되면 허브 PC 방화벽에서 포트를 허용합니다. `server`가 안내하는 `netsh` 명령을 **확인한 뒤 관리자 명령 프롬프트에서 직접 실행**하세요. (이 도구는 방화벽을 바꾸지 않습니다.)
3. 교무실 PC에서 `check`를 실행합니다. 같은 명령을 학생 노트북(독서실 와이파이)에서도 실행합니다.
4. 독서실 운영 시간을 포함해 `watch`를 돌려 끊기는 시간대를 기록합니다 (기본 24시간, 결과는 `netcheck_watch.csv`).
5. 테스트가 끝나면 방화벽 규칙을 삭제합니다: `netsh advfirewall firewall delete rule name="netcheck"`

## check 항목과 판정 (기준은 제안값)

| 번호 | 항목 | 합격 기준 |
|---|---|---|
| 1 | TCP 연결 | 지정 포트(기본 8000, 8080) 중 하나 이상 연결 |
| 2 | HTTP 왕복 | 20회 호출, 손실 0회, 평균 100ms 이하 (`-MaxAvg` / `--max-avg`로 조정) |
| 3 | POST 전송 | 1KB, 64KB 모두 정상 |
| 4 | 실시간 수신 | 30초간 1초 간격 메시지를 끊김 없이 수신, 최대 간격 2.5초 이하 |
| 참고 | ICMP ping | 판정에 포함하지 않음 (막혀 있는 경우가 많음) |

1~4가 모두 PASS이면 `A안 사용 가능`, 하나라도 FAIL이면 `A안 조치 필요`로 표시하고 종료 코드 1을 반환합니다.
FAIL이면 전산 담당과 협의해 다시 시험하고, 해결되지 않으면 B안(중계 서버)을 검토합니다.

## 스크립트 실행이 막힌 PC (수동 점검)

보안 정책으로 스크립트 실행이 막혀 있어도, 허브 PC에서 `server`가 실행 중이면 윈도우 기본 명령으로 최소한의 확인은 가능합니다.

| 목적 | 명령 (CMD) |
|---|---|
| 네트워크 응답 | `ping 192.168.0.10` |
| 포트 접속 | `powershell -Command "Test-NetConnection 192.168.0.10 -Port 8000"` (`TcpTestSucceeded : True`이면 성공) |
| HTTP 응답 | `curl.exe http://192.168.0.10:8000/ping` (`{"ok":true,...}`이 나오면 성공) |

수동 점검으로는 항목 1~2 정도만 확인할 수 있습니다. 실시간 수신과 장기 관찰은 스크립트가 필요합니다.

## 알아둘 점

- 두 버전 모두 **시스템 프록시를 쓰지 않고 직접 연결**합니다. A안은 직결 확인이 목적이고 학교망의 프록시 설정에 영향받지 않게 하기 위해서입니다.
- 개발 PC 한 대에서 PowerShell 서버/클라이언트, 파이썬 서버/클라이언트, 서로 섞은 조합, 실패 경로, 끊김 감지(`watch`)를 검증했습니다. **실제 교내망에서의 결과는 아직 없습니다.**
- 항목 4의 `/stream`은 1초마다 메시지를 보내는 연결을 유지합니다. 교사 대시보드의 실시간 알림이 같은 방식(연결 유지)으로 동작하므로, 중간 장비가 오래된 연결을 끊는지 미리 확인하는 용도입니다.
- 이 도구는 접속 가능 여부만 확인합니다. 인증과 암호화는 없으므로 테스트 때만 켜고 끝나면 종료하세요.
- `netcheck.ps1`은 **UTF-8 BOM** 형식으로 저장되어 있습니다. 편집기로 수정할 때 BOM을 빼고 저장하면 PowerShell 5.1에서 한글이 깨집니다.
