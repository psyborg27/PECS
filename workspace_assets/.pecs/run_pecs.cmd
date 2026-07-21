@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set CONFIG_FILE=%SCRIPT_DIR%config\install_root.json
set INSTALL_ROOT=
set INSTALL_PYTHON=
set PECS_EXE=
set IDX=0
set PYTHON_EXEC=python
where python >nul 2>&1 || set PYTHON_EXEC=py -3
for /f "usebackq delims=" %%A in (`%PYTHON_EXEC% -c "import json,sys; p=sys.argv[1]; data=json.loads(open(p,encoding='utf-8').read()); print(data.get('install_root','')); print(data.get('python_path','')); print(data.get('console_scripts',{}).get('pecs','')); print(data.get('console_scripts',{}).get('pecs-pro-daemon',''))" "%CONFIG_FILE%"`) do (
  set /a IDX+=1
  if !IDX! EQU 1 set INSTALL_ROOT=%%A
  if !IDX! EQU 2 set INSTALL_PYTHON=%%A
  if !IDX! EQU 3 set PECS_EXE=%%A
)
if defined PECS_EXE if exist "%PECS_EXE%" (
  "%PECS_EXE%" %*
  goto :EOF
)
if defined INSTALL_PYTHON if exist "%INSTALL_PYTHON%" (
  "%INSTALL_PYTHON%" -m workspace_bridge_cli %*
  goto :EOF
)
pecs %*
