$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$WorkspaceRoot = if ($args.Count -ge 1) { $args[0] } else { "." }
$RemainingArgs = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { Write-Error "Python is not available on PATH"; exit 1 }
& $python.Source (Join-Path $ScriptDir "append_ai_chat_history.py") $WorkspaceRoot @RemainingArgs
