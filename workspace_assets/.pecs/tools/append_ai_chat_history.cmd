@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set WORKSPACE_ROOT=%~1
shift
set SOURCE=%~1
shift
set MESSAGE=%*
if "%WORKSPACE_ROOT%"=="" set WORKSPACE_ROOT=.
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
"%PYTHON_EXEC%" "%SCRIPT_DIR%append_ai_chat_history.py" "%WORKSPACE_ROOT%" --source "!SOURCE!" --message "!MESSAGE!"
