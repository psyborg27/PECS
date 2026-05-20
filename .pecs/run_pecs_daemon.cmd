@echo off
setlocal enabledelayedexpansion
set WORKSPACE_ROOT=%~1
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
set SCRIPT_DIR=%~dp0
set LAUNCHER=%SCRIPT_DIR%run_pecs_daemon.ps1
if exist "%LAUNCHER%" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%" "%WORKSPACE_ROOT%"
  goto :EOF
)
echo ERROR: Workspace daemon launcher missing: %LAUNCHER%
exit /b 1
