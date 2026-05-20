param(
    [string]$WorkspaceRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path $ScriptDir

function Throw-Error {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Resolve-WorkspaceRoot {
    param([string]$PathValue)
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return $null
    }
    try {
        $resolved = Resolve-Path -Path $PathValue -ErrorAction Stop
        if (-not (Test-Path $resolved.Path -PathType Container)) {
            return $null
        }
        return $resolved.Path
    } catch {
        return $null
    }
}

function Prompt-WorkspaceRoot {
    param([string]$InitialPath)
    $root = $InitialPath
    while ($true) {
        if ([string]::IsNullOrWhiteSpace($root)) {
            $root = Read-Host 'Enter the target workspace root path'
        }
        $resolved = Resolve-WorkspaceRoot -PathValue $root
        if ($resolved) {
            return $resolved
        }
        Write-Host "Workspace does not exist or is not a folder: $root" -ForegroundColor Yellow
        $root = ''
    }
}

function Confirm-PecsVisibility {
    $answer = Read-Host 'Is the .pecs folder visible in the workspace explorer? [y/N]'
    switch ($answer.ToLower()) {
        'y' { return }
        'yes' { return }
        default {
            Throw-Error 'Please verify your workspace path and rerun setup.'
        }
    }
}

$WorkspaceRoot = Prompt-WorkspaceRoot $WorkspaceRoot

$pecsDir = Join-Path -Path $WorkspaceRoot -ChildPath '.pecs'
if (-not (Test-Path $pecsDir)) {
    New-Item -ItemType Directory -Path $pecsDir -Force | Out-Null
}
Write-Host "Created or verified .pecs folder: $pecsDir"
Confirm-PecsVisibility

$pythonCommand = (Get-Command python3 -ErrorAction SilentlyContinue).Source
if (-not $pythonCommand) {
    $pythonCommand = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $pythonCommand) {
    $pythonCommand = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $pythonCommand) {
    Throw-Error 'Python is not available on PATH. Install Python 3 or ensure python/py is in PATH.'
}

$venvDir = Join-Path $RepoRoot '.venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Host 'Creating Python virtual environment in .venv...'
    & $pythonCommand -m venv $venvDir
}

if (-not (Test-Path $venvPython)) {
    Throw-Error "Virtual environment python not found at $venvPython"
}

Write-Host 'Upgrading pip, setuptools, and wheel...'
& $venvPython -m pip install --upgrade pip setuptools wheel

if (Test-Path (Join-Path $RepoRoot 'requirements.txt')) {
    Write-Host 'Installing required dependencies...'
    & $venvPython -m pip install -r (Join-Path $RepoRoot 'requirements.txt')
}

Write-Host 'Installing PECS-PRO in editable mode...'
& $venvPython -m pip install -e $RepoRoot

Write-Host "Bootstrapping workspace: $WorkspaceRoot"
& $venvPython -m workspace_bridge_cli bootstrap-workspace $WorkspaceRoot --repo-root $RepoRoot --upgrade

Write-Host 'PECS onboarding completed successfully.'
Write-Host "Run: $venvPython -m workspace_bridge_cli status $WorkspaceRoot"