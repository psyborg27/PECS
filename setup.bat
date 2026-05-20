@echo off
setlocal enabledelayedexpansion

set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"
set "REPO_ROOT=%CD%"

set "WORKSPACE_ROOT=%~1"
if "%WORKSPACE_ROOT%"=="" (
  set /p "WORKSPACE_ROOT=Enter the target workspace root path: "
)

:ValidateWorkspace
if "%WORKSPACE_ROOT%"=="" (
  echo Workspace path is required.
  set /p "WORKSPACE_ROOT=Enter the target workspace root path: "
)
if not exist "%WORKSPACE_ROOT%\" (
  echo Workspace does not exist or is not a folder: %WORKSPACE_ROOT%
  set "WORKSPACE_ROOT="
  goto ValidateWorkspace
)

rem Normalize path
for %%I in ("%WORKSPACE_ROOT%") do set "WORKSPACE_ROOT=%%~fI"

if not exist "%WORKSPACE_ROOT%\.pecs" (
  mkdir "%WORKSPACE_ROOT%\.pecs" >nul 2>&1
  if errorlevel 1 (
    echo ERROR: Failed to create .pecs in %WORKSPACE_ROOT%
    exit /b 1
  )
)

echo .pecs folder created or verified at %WORKSPACE_ROOT%\.pecs

:ConfirmPecs
set /p "PEC_CONFIRM=Is the .pecs folder visible in the workspace explorer? [y/N]: "
if /i "%PEC_CONFIRM%"=="Y" goto Confirmed
if /i "%PEC_CONFIRM%"=="YES" goto Confirmed
if /i "%PEC_CONFIRM%"=="N" (
  echo Please re-enter the correct workspace root path.
  set /p "WORKSPACE_ROOT=Workspace root: "
  goto ValidateWorkspace
)
if /i "%PEC_CONFIRM%"=="NO" (
  echo Please re-enter the correct workspace root path.
  set /p "WORKSPACE_ROOT=Workspace root: "
  goto ValidateWorkspace
)
echo Please answer y or n.
goto ConfirmPecs

:Confirmed

where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo ERROR: Python is not available on PATH.
    exit /b 1
  ) else (
    set "PYTHON_CMD=py -3"
  )
) else (
  set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment in .venv...
  %PYTHON_CMD% -m venv ".venv"
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Virtual environment python not found at .venv\Scripts\python.exe
  exit /b 1
)

set "VENV_PYTHON=.venv\Scripts\python.exe"

echo Upgrading pip, setuptools, and wheel...
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel

if exist "requirements.txt" (
  echo Installing required dependencies...
  "%VENV_PYTHON%" -m pip install -r "requirements.txt"
)

echo Installing PECS-PRO in editable mode...
"%VENV_PYTHON%" -m pip install -e "%REPO_ROOT%"

echo Bootstrapping workspace: %WORKSPACE_ROOT%
"%VENV_PYTHON%" -m workspace_bridge_cli bootstrap-workspace "%WORKSPACE_ROOT%" --repo-root "%REPO_ROOT%" --upgrade

echo PECS onboarding completed successfully.
echo Run: "%VENV_PYTHON%" -m workspace_bridge_cli status "%WORKSPACE_ROOT%"
