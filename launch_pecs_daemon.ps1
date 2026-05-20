<#
.SYNOPSIS
Launch the PECS daemon for a Windows workspace.
#>
[CmdletBinding()]
param(
    [string]$WorkspaceRoot = '.'
)

Set-StrictMode -Version Latest

$WorkspacePath = Resolve-Path -Path $WorkspaceRoot -ErrorAction Stop
$WorkspaceRoot = $WorkspacePath.Path
$Launcher = Join-Path -Path $WorkspaceRoot -ChildPath ".pecs\run_pecs_daemon.ps1"

if (-not (Test-Path $Launcher)) {
    throw "ERROR: Workspace daemon launcher missing: $Launcher`nRun install-workspace-assets or bootstrap-workspace first."
}

& $Launcher $WorkspaceRoot
