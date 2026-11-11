<#
.SYNOPSIS
  A안(교내망 직결) 접속 테스트 - PowerShell 버전 (윈도우 10/11 기본 PowerShell 5.1, 추가 설치 없음)

.DESCRIPTION
  netcheck.py 와 같은 통신 규격이라 서로 섞어서 쓸 수 있다 (예: 허브는 파이썬 server, 교무실은 PowerShell check).

  netcheck.cmd server                      [허브 PC]   테스트 서버 시작
  netcheck.cmd check <허브 IP>             [교무실 PC] 접속 테스트 (항목 1~4 판정)
  netcheck.cmd watch <허브 IP>             [장기 관찰] 끊김 기록 (기본 24시간)
  netcheck.cmd info                        내 IP 확인

  옵션: -Ports 8000,8080  -Count 20  -StreamSec 30  -MaxAvg 100  -Report report.json
        -Port 8000 -Interval 10 -Duration 86400 -Csv netcheck_watch.csv   (watch)
#>
param(
    [Parameter(Position = 0)][ValidateSet('server', 'check', 'watch', 'info')][string]$Mode = 'info',
    [Parameter(Position = 1)][string]$HubIP,
    [string]$Ports = '8000,8080',
    [int]$Port = 8000,
    [int]$Count = 20,
    [int]$StreamSec = 30,
    [double]$MaxAvg = 100,
    [double]$Interval = 10,
    [double]$Duration = 86400,
    [string]$Report,
    [string]$Csv = 'netcheck_watch.csv'
)

$ErrorActionPreference = 'Stop'
$MaxStreamGap = 2.5   # 합격 기준(제안): 실시간 수신 간격 최대(초). 서버는 1초마다 보낸다.

function Now { (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') }
function Parse-Ports([string]$t) { @($t -split ',' | Where-Object { $_.Trim() } | ForEach-Object { [int]$_.Trim() }) }
function Get-LocalIPs {
    @([System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
        Where-Object { $_.AddressFamily -eq 'InterNetwork' } | ForEach-Object { $_.ToString() })
}
function My-IpToward([string]$hub) {
    $u = New-Object System.Net.Sockets.UdpClient
    try { $u.Connect($hub, 9); return $u.Client.LocalEndPoint.Address.ToString() }
    catch { return '?' } finally { $u.Close() }
}
function Err-Name($ex) {
    $b = $ex.GetBaseException()
    if ($b -is [System.Net.Sockets.SocketException]) { return $b.SocketErrorCode.ToString() }
    return $b.GetType().Name
}

# ============================================================ 서버 (허브 PC)
function Read-Request($client) {
    $stream = $client.GetStream()
    $stream.ReadTimeout = 2000
    $buf = New-Object byte[] 8192
    $ms = New-Object System.IO.MemoryStream
    $headerEnd = -1
    while ($headerEnd -lt 0) {
        $n = $stream.Read($buf, 0, $buf.Length)
        if ($n -le 0) { return $null }
        $ms.Write($buf, 0, $n)
        $headerEnd = [System.Text.Encoding]::ASCII.GetString($ms.ToArray()).IndexOf("`r`n`r`n")
    }
    $head = [System.Text.Encoding]::ASCII.GetString($ms.ToArray(), 0, $headerEnd)
    $first = ($head -split "`r`n")[0] -split ' '
    $len = 0
    if ($head -match '(?im)^Content-Length:\s*(\d+)') { $len = [int]$Matches[1] }
    $have = $ms.Length - ($headerEnd + 4)
    while ($have -lt $len) {
        $n = $stream.Read($buf, 0, $buf.Length)
        if ($n -le 0) { break }
        $have += $n
    }
    return @{ Method = $first[0]; Path = $first[1]; BodyLen = [int]$len }
}

function Send-Json($stream, [int]$code, $obj) {
    $body = [System.Text.Encoding]::UTF8.GetBytes(($obj | ConvertTo-Json -Compress))
    $reason = 'OK'
    if ($code -ne 200) { $reason = 'Not Found' }
    $hb = [System.Text.Encoding]::ASCII.GetBytes("HTTP/1.0 $code $reason`r`nContent-Type: application/json`r`nContent-Length: $($body.Length)`r`n`r`n")
    $stream.Write($hb, 0, $hb.Length)
    $stream.Write($body, 0, $body.Length)
    $stream.Flush()
}

function Run-Server {
    $portList = Parse-Ports $Ports
    $listeners = @()
    foreach ($p in $portList) {
        try {
            $l = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $p)
            $l.Start()
            $listeners += $l
        } catch { Write-Host "[오류] 포트 $p 를 열 수 없습니다: $($_.Exception.Message)" }
    }
    if ($listeners.Count -eq 0) { exit 1 }
    $opened = ($listeners | ForEach-Object { ([System.Net.IPEndPoint]$_.LocalEndpoint).Port }) -join ','
    Write-Host "[$(Now)] 테스트 서버 시작  포트: $opened  (종료: Ctrl+C)"
    Write-Host '이 PC의 IP 주소 (교무실 PC에서 입력):'
    foreach ($ip in (Get-LocalIPs)) { Write-Host "    $ip" }
    Write-Host ''
    Write-Host '접속이 안 되면 이 PC의 방화벽에서 포트를 허용하세요 (관리자 명령 프롬프트, 확인만 하고 직접 실행):'
    Write-Host "    netsh advfirewall firewall add rule name=`"netcheck`" dir=in action=allow protocol=TCP localport=$opened"
    Write-Host ''

    $streams = New-Object System.Collections.ArrayList
    try {
        while ($true) {
            foreach ($l in $listeners) {
                while ($l.Pending()) {
                    $c = $l.AcceptTcpClient()
                    $keep = $false
                    try {
                        $ip = ([System.Net.IPEndPoint]$c.Client.RemoteEndPoint).Address.ToString()
                        $req = Read-Request $c
                        if ($null -ne $req) {
                            Write-Host ("[{0}] {1,15}  {2} {3}" -f (Now), $ip, $req.Method, $req.Path)
                            $stream = $c.GetStream()
                            $path = ($req.Path -split '\?')[0]
                            if ($req.Method -eq 'GET' -and $path -eq '/ping') {
                                $lp = ([System.Net.IPEndPoint]$c.Client.LocalEndPoint).Port
                                Send-Json $stream 200 @{ ok = $true; server_time = [double]([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0); port = $lp }
                            } elseif ($req.Method -eq 'POST' -and $path -eq '/echo') {
                                Send-Json $stream 200 @{ ok = $true; len = $req.BodyLen }
                            } elseif ($req.Method -eq 'GET' -and $path -eq '/stream') {
                                $sec = 30
                                if ($req.Path -match 'sec=(\d+)') { $sec = [int]$Matches[1] }
                                $hb = [System.Text.Encoding]::ASCII.GetBytes("HTTP/1.0 200 OK`r`nContent-Type: text/event-stream`r`nCache-Control: no-cache`r`n`r`n")
                                $stream.Write($hb, 0, $hb.Length)
                                [void]$streams.Add(@{ Client = $c; Stream = $stream; Next = [DateTime]::UtcNow; Sent = 0; Total = $sec })
                                $keep = $true
                            } else {
                                Send-Json $stream 404 @{ ok = $false; error = 'not found' }
                            }
                        }
                    } catch { }
                    if (-not $keep) { try { $c.Close() } catch { } }
                }
            }
            for ($i = $streams.Count - 1; $i -ge 0; $i--) {
                $s = $streams[$i]
                if ([DateTime]::UtcNow -ge $s.Next) {
                    $done = $false
                    try {
                        $t = [double]([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0)
                        $b = [System.Text.Encoding]::ASCII.GetBytes(("data: {0} {1:F3}`n`n" -f $s.Sent, $t))
                        $s.Stream.Write($b, 0, $b.Length)
                        $s.Stream.Flush()
                        $s.Sent++
                        $s.Next = $s.Next.AddSeconds(1)
                        if ($s.Sent -ge $s.Total) { $done = $true }
                    } catch { $done = $true }
                    if ($done) { try { $s.Client.Close() } catch { }; $streams.RemoveAt($i) }
                }
            }
            Start-Sleep -Milliseconds 20
        }
    } finally {
        foreach ($l in $listeners) { $l.Stop() }
        Write-Host "`n종료합니다."
    }
}

# ============================================================ 클라이언트
function Http-Request([string]$method, [string]$url, [byte[]]$body, [int]$timeoutMs) {
    $req = [System.Net.HttpWebRequest]::Create($url)
    $req.Method = $method
    $req.Proxy = $null            # 시스템 프록시를 쓰지 않고 직접 연결 (A안은 직결 확인이 목적)
    $req.Timeout = $timeoutMs
    $req.ReadWriteTimeout = $timeoutMs
    $req.KeepAlive = $false
    if ($null -ne $body) {
        $req.ContentLength = $body.Length
        $rs = $req.GetRequestStream(); $rs.Write($body, 0, $body.Length); $rs.Close()
    }
    $resp = $req.GetResponse()
    $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
    $text = $sr.ReadToEnd()
    $sr.Close(); $resp.Close()
    return $text
}

function Test-Tcp([string]$ip, [int]$port, [int]$timeoutMs = 3000) {
    $c = New-Object System.Net.Sockets.TcpClient
    $sw = [Diagnostics.Stopwatch]::StartNew()
    try {
        $iar = $c.BeginConnect($ip, $port, $null, $null)
        if ($iar.AsyncWaitHandle.WaitOne($timeoutMs)) {
            $c.EndConnect($iar)
            return @{ Ok = $true; Ms = $sw.Elapsed.TotalMilliseconds; Err = '' }
        }
        return @{ Ok = $false; Ms = 0; Err = 'Timeout' }
    } catch {
        return @{ Ok = $false; Ms = 0; Err = (Err-Name $_.Exception) }
    } finally { $c.Close() }
}

$script:items = @()
function Add-Item($no, $name, $status, $detail) {
    $script:items += [pscustomobject]@{ no = "$no"; name = $name; status = $status; detail = $detail }
    Write-Host ("[{0,-4}] {1}. {2}: {3}" -f $status, $no, $name, $detail)
}

function Finish {
    $judged = @($script:items | Where-Object { $_.status -eq 'PASS' -or $_.status -eq 'FAIL' })
    $failed = @($judged | Where-Object { $_.status -eq 'FAIL' })
    $ok = ($judged.Count -ge 4) -and ($failed.Count -eq 0)
    Write-Host ("`n" + ('=' * 60))
    if ($ok) { Write-Host '판정: A안 사용 가능 (항목 1~4 모두 PASS)' }
    else { Write-Host '판정: A안 조치 필요  ->  전산 담당과 협의 후 재시험, 해결이 안 되면 B안(중계 서버) 검토' }
    Write-Host ('=' * 60)
    if ($Report) {
        $obj = [ordered]@{ time = (Now); host = $HubIP; ports = (Parse-Ports $Ports); a_plan_ok = $ok; items = $script:items }
        ($obj | ConvertTo-Json -Depth 4) | Out-File -FilePath $Report -Encoding UTF8
        Write-Host "결과 파일 저장: $Report"
    }
    if ($ok) { exit 0 } else { exit 1 }
}

function Run-Check {
    if (-not $HubIP) { Write-Host '허브 IP 를 입력하세요.  예: netcheck.cmd check 192.168.0.10'; exit 2 }
    $portList = Parse-Ports $Ports
    Write-Host "[$(Now)] 접속 테스트 시작  대상: $HubIP  포트: $($portList -join ',')"
    Write-Host "    이 PC의 IP: $(My-IpToward $HubIP)   (같은 네트워크 대역인지 허브 IP와 앞 3자리를 비교하세요)"
    Write-Host ''

    # 1. TCP 연결
    $parts = @(); $okPorts = @()
    foreach ($p in $portList) {
        $r = Test-Tcp $HubIP $p
        if ($r.Ok) { $okPorts += $p; $parts += ('{0}:OK({1:N0}ms)' -f $p, $r.Ms) }
        else { $parts += ('{0}:FAIL({1})' -f $p, $r.Err) }
    }
    $st = 'FAIL'; if ($okPorts.Count -gt 0) { $st = 'PASS' }
    Add-Item 1 'TCP 연결' $st ($parts -join '  ')
    if ($okPorts.Count -eq 0) {
        Write-Host ''
        Write-Host '허브 서버에 연결할 수 없습니다. 확인할 것:'
        Write-Host '  - 허브 PC에서 server 가 실행 중인지, IP 주소가 맞는지'
        Write-Host '  - 허브 PC 방화벽이 포트를 막고 있는지'
        Write-Host '  - 교무실과 독서실이 서로 다른 네트워크(VLAN)라서 막혀 있는지 -> 전산 담당에게 문의'
        Finish
    }
    $base = "http://${HubIP}:$($okPorts[0])"

    # 2. HTTP 왕복
    $rtts = @(); $fails = 0
    for ($i = 0; $i -lt $Count; $i++) {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        try { [void](Http-Request 'GET' "$base/ping" $null 3000); $rtts += $sw.Elapsed.TotalMilliseconds }
        catch { $fails++ }
        Start-Sleep -Milliseconds 200
    }
    if ($rtts.Count -gt 0) {
        $m = $rtts | Measure-Object -Average -Minimum -Maximum
        $st = 'FAIL'; if ($fails -eq 0 -and $m.Average -le $MaxAvg) { $st = 'PASS' }
        Add-Item 2 'HTTP 왕복' $st ('{0}회 중 손실 {1}회, 지연 최소/평균/최대 = {2:N0}/{3:N0}/{4:N0} ms (기준: 손실 0, 평균 {5:N0}ms 이하)' -f $Count, $fails, $m.Minimum, $m.Average, $m.Maximum, $MaxAvg)
    } else { Add-Item 2 'HTTP 왕복' 'FAIL' '응답 없음' }

    # 3. POST 전송
    $bad = @()
    foreach ($n in @(1024, 65536)) {
        try {
            $resp = Http-Request 'POST' "$base/echo" (New-Object byte[] $n) 5000
            if (($resp | ConvertFrom-Json).len -ne $n) { $bad += "${n}B 길이 불일치" }
        } catch { $bad += "${n}B $(Err-Name $_.Exception)" }
    }
    if ($bad.Count -gt 0) { Add-Item 3 'POST 전송' 'FAIL' ($bad -join ', ') }
    else { Add-Item 3 'POST 전송' 'PASS' '1KB, 64KB 모두 정상' }

    # 4. 실시간 수신 (교사 알림용 연결 유지)
    Write-Host "      ... 실시간 수신 ${StreamSec}초 측정 중"
    $times = New-Object System.Collections.ArrayList; $err = ''
    try {
        $req = [System.Net.HttpWebRequest]::Create("$base/stream?sec=$StreamSec")
        $req.Proxy = $null; $req.Timeout = 5000; $req.ReadWriteTimeout = 5000
        $resp = $req.GetResponse()
        $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $sw = [Diagnostics.Stopwatch]::StartNew()
        while ($true) {
            $line = $sr.ReadLine()
            if ($null -eq $line) { break }
            if ($line.StartsWith('data:')) { [void]$times.Add($sw.Elapsed.TotalSeconds) }
        }
        $sr.Close(); $resp.Close()
    } catch { $err = Err-Name $_.Exception }
    $maxGap = 0.0
    for ($i = 1; $i -lt $times.Count; $i++) { $g = $times[$i] - $times[$i - 1]; if ($g -gt $maxGap) { $maxGap = $g } }
    $st = 'FAIL'; if (($err -eq '') -and ($times.Count -ge $StreamSec) -and ($maxGap -le $MaxStreamGap)) { $st = 'PASS' }
    $d = '{0}/{1}건 수신, 최대 간격 {2:N1}초' -f $times.Count, $StreamSec, $maxGap
    if ($err) { $d += ", 오류 $err" }
    Add-Item 4 '실시간 수신' $st $d

    # 참고. ICMP ping (판정에 영향 없음)
    try {
        $ping = Test-Connection -ComputerName $HubIP -Count 2 -Quiet
        $msg = '응답 없음 (막혀 있어도 A안 판정에는 영향 없음)'; if ($ping) { $msg = '응답 있음' }
        Add-Item '-' 'ICMP ping (참고)' 'INFO' $msg
    } catch { Add-Item '-' 'ICMP ping (참고)' 'INFO' '실행 불가' }
    Finish
}

function Run-Watch {
    if (-not $HubIP) { Write-Host '허브 IP 를 입력하세요.  예: netcheck.cmd watch 192.168.0.10'; exit 2 }
    $url = "http://${HubIP}:$Port/ping"
    $end = (Get-Date).AddSeconds($Duration)
    $state = $null; $downSince = $null; $outages = @(); $total = 0; $success = 0
    Write-Host "[$(Now)] 장기 관찰 시작  대상: $url  간격: ${Interval}초  기간: ${Duration}초  (종료: Ctrl+C)"
    Set-Content -Path $Csv -Value '시각,성공,지연(ms),오류' -Encoding UTF8
    try {
        while ((Get-Date) -lt $end) {
            $ts = Now; $ok = $true; $rtt = ''; $err = ''
            $sw = [Diagnostics.Stopwatch]::StartNew()
            try { [void](Http-Request 'GET' $url $null 3000); $rtt = '{0:N0}' -f $sw.Elapsed.TotalMilliseconds }
            catch { $ok = $false; $err = Err-Name $_.Exception }
            $total++; if ($ok) { $success++ }
            Add-Content -Path $Csv -Value ("{0},{1},{2},{3}" -f $ts, [int]$ok, $rtt, $err) -Encoding UTF8
            if ($state -ne $ok) {
                if ($ok) { Write-Host "[$ts] 연결됨" } else { Write-Host "[$ts] 끊김 ($err)" }
                if (-not $ok) { $downSince = $ts }
                elseif ($downSince) { $outages += ,@($downSince, $ts); $downSince = $null }
                $state = $ok
            }
            Start-Sleep -Milliseconds ([int]($Interval * 1000))
        }
    } finally {
        if ($downSince) { $outages += ,@($downSince, ((Now) + ' (관찰 종료 시점까지 끊김)')) }
        $pct = 0.0; if ($total -gt 0) { $pct = 100.0 * $success / $total }
        Write-Host ("`n" + ('=' * 60))
        Write-Host ('관찰 {0}회, 성공 {1}회 ({2:N1}%), 끊긴 구간 {3}건' -f $total, $success, $pct, $outages.Count)
        foreach ($o in $outages) { Write-Host "    $($o[0])  ~  $($o[1])" }
        Write-Host "기록 파일: $Csv"
        Write-Host ('=' * 60)
    }
    if ($outages.Count -gt 0) { exit 1 } else { exit 0 }
}

switch ($Mode) {
    'server' { Run-Server }
    'check'  { Run-Check }
    'watch'  { Run-Watch }
    default {
        Write-Host '이 PC의 IP 주소:'
        foreach ($ip in (Get-LocalIPs)) { Write-Host "    $ip" }
        Write-Host ''
        Write-Host '사용법:'
        Write-Host '    netcheck.cmd server                허브 PC에서 테스트 서버 시작'
        Write-Host '    netcheck.cmd check <허브 IP>       접속 테스트'
        Write-Host '    netcheck.cmd watch <허브 IP>       장기 관찰 (끊김 기록)'
    }
}
