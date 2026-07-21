$args = $args
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Command = if ($args.Count -ge 1) { $args[0] } else { "refresh" }
$WorkspaceRoot = if ($args.Count -ge 2) { $args[1] } else { "." }
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { Write-Error "Python is not available on PATH"; exit 1 }
& $python.Source (Join-Path $ScriptDir "run_bridge.py") $Command --workspace $WorkspaceRoot
