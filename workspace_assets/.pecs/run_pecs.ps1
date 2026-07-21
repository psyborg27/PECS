$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = $null
$InstallPython = $null
$PecsExe = $null
$PecsDaemonExe = $null
$ConfigFile = Join-Path $ScriptDir "config" "install_root.json"
if (Test-Path $ConfigFile) {
  $data = Get-Content $ConfigFile -Raw | ConvertFrom-Json
  $InstallRoot = $data.install_root
  $InstallPython = $data.python_path
  $PecsExe = $data.console_scripts.pecs
  $PecsDaemonExe = $data.console_scripts."pecs-pro-daemon"
}
$WorkspaceArgs = $args
if ($PecsExe -and (Test-Path $PecsExe)) {
  & $PecsExe @WorkspaceArgs
  exit $LASTEXITCODE
}
if ($InstallPython -and (Test-Path $InstallPython)) {
  & $InstallPython -m workspace_bridge_cli @WorkspaceArgs
  exit $LASTEXITCODE
}
Write-Error "ERROR: Could not resolve PECS runtime from install root or PATH."
Write-Error "Expected install root: $InstallRoot"
exit 1
