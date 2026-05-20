<#
.SYNOPSIS
Install PECS and bootstrap a Windows workspace interactively.
#>
[CmdletBinding()]
param(
    [string]$WorkspaceRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent

function Throw-InstallerError {
    param([string]$Message)
    Write-Error $Message
    Write-Error 'Copy the full error output, include OS/version, branch name, and report the issue on GitHub.'
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
    while ($true) {
        if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
            $WorkspaceRoot = Read-Host 'Enter the target workspace root path'
        }

        $resolved = Resolve-WorkspaceRoot -PathValue $WorkspaceRoot
        if (-not $resolved) {
            Write-Host "Workspace does not exist or is not a folder: $WorkspaceRoot" -ForegroundColor Yellow
            $WorkspaceRoot = ''
            continue
        }

        $WorkspaceRoot = $resolved
        try {
            $pecsDir = Join-Path -Path $WorkspaceRoot -ChildPath '.pecs'
            if (-not (Test-Path $pecsDir)) {
                New-Item -ItemType Directory -Path $pecsDir -Force | Out-Null
            }
        } catch {
            Write-Host "Workspace path is not writable or .pecs cannot be created: $WorkspaceRoot" -ForegroundColor Red
            $WorkspaceRoot = ''
            continue
        }

        return
    }
}

function Confirm-PecsVisibility {
    while ($true) {
        $answer = Read-Host 'Is the .pecs folder visible in the workspace explorer? [y/N]'
        switch ($answer.ToLower()) {
            'y' { return }
            'yes' { return }
            'n' { 
                $WorkspaceRoot = Read-Host 'Please re-enter the correct workspace root path'
                if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
                    Throw-InstallerError 'Installer aborted by user.'
                }
                Prompt-WorkspaceRoot
                continue
            }
            default {
                Write-Host 'Please answer y or n.' -ForegroundColor Yellow
            }
        }
    }
}

$WorkspaceRoot = Resolve-WorkspaceRoot -PathValue $WorkspaceRoot
Prompt-WorkspaceRoot

$pecsDir = Join-Path -Path $WorkspaceRoot -ChildPath '.pecs'
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
    Throw-InstallerError 'Python is not available on PATH. Install Python 3 or ensure python/py is in PATH.'
}

$workspaceArgs = @('bootstrap-workspace', $WorkspaceRoot, '--repo-root', $RepoRoot, '--upgrade')
Write-Host "Bootstrapping workspace: $WorkspaceRoot"
Push-Location -Path $RepoRoot
try {
    & $pythonCommand -m workspace_bridge_cli @workspaceArgs
    Write-Host 'Workspace bootstrap completed successfully.'
    Write-Host "Verify with: & $pythonCommand -m workspace_bridge_cli status '$WorkspaceRoot'"
} catch {
    Throw-InstallerError "Workspace bootstrap failed: $($_.Exception.Message)"
} finally {
    Pop-Location
}
