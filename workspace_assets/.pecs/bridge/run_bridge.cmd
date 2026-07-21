@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set WORKSPACE_ROOT=%~1
set COMMAND=%~2
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
if "%COMMAND%"=="" set COMMAND=refresh
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
"%PYTHON_EXEC%" "%SCRIPT_DIR%run_bridge.py" "%COMMAND%" --workspace "%WORKSPACE_ROOT%"
