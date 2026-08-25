<#
.SYNOPSIS
    vibe-editing.ps1 "<youtube-url-or-file>"  ->  finished vertical clips in a folder.

.DESCRIPTION
    Thin wrapper around Claude Code running the /edit workflow autonomously.
#>
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Source
)

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host 'Claude Code CLI not found. Install it, then run:  /edit ' -NoNewline
    Write-Host ($Source -join ' ')
    exit 1
}

$target = $Source -join ' '
claude "Use the vibe-editing /edit workflow to turn this into finished, captioned, audited vertical clips fully autonomously, then tell me where they were delivered: $target"
