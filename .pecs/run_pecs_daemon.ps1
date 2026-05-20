param([string]$WorkspaceRoot = ".")
Set-StrictMode -Version Latest

$WorkspacePath = Resolve-Path -Path $WorkspaceRoot -ErrorAction Stop
$WorkspaceRoot = $WorkspacePath.Path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ConfigFile = Join-Path $ScriptDir "config" "install_root.json"
$InstallRoot = $null
$InstallPython = $null
$PecsDaemonExe = $null

if (Test-Path $ConfigFile) {
  $data = Get-Content $ConfigFile -Raw | ConvertFrom-Json
  $InstallRoot = $data.install_root
  $InstallPython = $data.python_path
  $PecsDaemonExe = $data.console_scripts."pecs-pro-daemon"
}

$PecsRoot = Join-Path $WorkspaceRoot ".pecs"
$LogFile = Join-Path $PecsRoot "daemon.log"
$PidFile = Join-Path $PecsRoot "daemon.pid"
$StartupTimeout = 10
$StartupInterval = 0.5

New-Item -ItemType Directory -Force -Path $PecsRoot | Out-Null

function Normalize-Pid {
    param([string]$RawPid)
    if ($RawPid -eq $null) {
      return $null
    }
    $value = $RawPid.Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
      $value = $value.Trim('"')
    }
    if ($value.StartsWith("'") -and $value.EndsWith("'")) {
      $value = $value.Trim("'")
    }
    return $value
  }

  if (Test-Path $PidFile) {
  try {
    $pid = Normalize-Pid (Get-Content $PidFile | Select-Object -First 1)
    if ($pid -match '^[0-9]+$' -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
      Write-Host "PECS daemon is already running for workspace: $WorkspaceRoot (pid=$pid)"
      exit 0
    }
  } catch {
    # ignore stale PID file content
  }
  Remove-Item -Force -Path $PidFile -ErrorAction SilentlyContinue
}

function Resolve-DaemonCommand {
  if ($PecsDaemonExe -and (Test-Path $PecsDaemonExe)) {
    return $PecsDaemonExe
  }
  if (Get-Command pecs-pro-daemon -ErrorAction SilentlyContinue) {
    return (Get-Command pecs-pro-daemon).Source
  }
  if ($InstallPython -and (Test-Path $InstallPython)) {
    return $InstallPython
  }
  return $null
}

$DaemonCmd = Resolve-DaemonCommand
if (-not $DaemonCmd) {
  Write-Error "ERROR: Could not resolve PECS daemon runtime from install root or PATH."
  Write-Error "Expected install root: $InstallRoot"
  exit 1
}

if ($DaemonCmd -eq $InstallPython) {
  $ArgumentList = @('-m', 'run_pecs_daemon', $WorkspaceRoot)
} else {
  $ArgumentList = @($WorkspaceRoot)
}

$process = Start-Process -FilePath $DaemonCmd -ArgumentList $ArgumentList -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile -NoNewWindow -WindowStyle Hidden -PassThru

$endTime = (Get-Date).AddSeconds($StartupTimeout)
while ((Get-Date) -lt $endTime) {
  Start-Sleep -Seconds $StartupInterval
  if (Test-Path $PidFile) {
    try {
      $pid = Normalize-Pid (Get-Content $PidFile | Select-Object -First 1)
      if ($pid -match '^[0-9]+$' -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
        Write-Host "Daemon started successfully (PID $pid)"
        exit 0
      }
    } catch {
      # continue waiting
    }
  }
  if ($process.HasExited) {
    Write-Error "Daemon process exited before startup. Check $LogFile"
    exit $process.ExitCode
  }
}

Write-Error "Daemon startup timed out waiting for .pecs/daemon.pid. See $LogFile"
exit 1
