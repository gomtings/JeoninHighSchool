@echo off
rem Plan-A network check (runs netcheck.ps1, no Python needed)
rem   netcheck.cmd server ^| check ^<hub-ip^> ^| watch ^<hub-ip^> ^| info
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0netcheck.ps1" %*
exit /b %errorlevel%
