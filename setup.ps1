<#
.SYNOPSIS
    One-command setup for Vibe Editing on Windows.

.DESCRIPTION
    Installs the system tools via winget, creates the Python virtualenv, installs the
    Python dependencies, and runs the health check. Safe to re-run: winget skips packages
    already present and pip skips satisfied requirements.

    NOTE: this file is deliberately ASCII-only. Windows PowerShell 5.1 reads a UTF-8
    script without a BOM as ANSI, so any dash or arrow here would render as mojibake.

.EXAMPLE
    .\setup.ps1
    .\setup.ps1 -SkipWinget        # deps only, if you installed the tools yourself
    .\setup.ps1 -IncludeOptional   # also tesseract, rclone, node
#>
[CmdletBinding()]
param(
    [switch]$SkipWinget,
    [switch]$IncludeOptional
)

$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$plug = Join-Path $dir 'plugins\vibe-editing'

function Update-PathFromRegistry {
    <#
      winget writes new tool locations to the *stored* user PATH, which an already-running
      process never sees. Without this the health check at the end of a first-time setup
      reports every tool it just installed as MISSING and tells the user to open a new
      terminal. Re-reading both scopes makes setup work in one pass.
    #>
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = (@($machine, $user) | Where-Object { $_ }) -join ';'
}

Write-Host ''
Write-Host '== Vibe Editing setup (Windows) ==' -ForegroundColor Cyan
Write-Host ''

# ---- 1. system tools --------------------------------------------------------
# Gyan.FFmpeg is the FULL build. A minimal ffmpeg lacks libass and cannot burn captions,
# which is the whole point of the kit, so doctor.py checks for libass specifically.
$core = @(
    @{ Id = 'Gyan.FFmpeg';   Name = 'ffmpeg (encode + burn captions)' },
    @{ Id = 'yt-dlp.yt-dlp'; Name = 'yt-dlp (download from a URL)' }
)
$optional = @(
    @{ Id = 'UB-Mannheim.TesseractOCR'; Name = 'tesseract (caption OCR audit)' },
    @{ Id = 'Rclone.Rclone';            Name = 'rclone (Google Drive footage pull)' },
    @{ Id = 'OpenJS.NodeJS.LTS';        Name = 'node (promo / Remotion skill)' }
)
$packages = if ($IncludeOptional) { $core + $optional } else { $core }

if ($SkipWinget) {
    Write-Host 'Skipping winget installs (-SkipWinget).' -ForegroundColor Yellow
} elseif (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host '!! winget not found. Install "App Installer" from the Microsoft Store,' -ForegroundColor Red
    Write-Host '   then re-run. Or install ffmpeg + yt-dlp yourself and use -SkipWinget.' -ForegroundColor Red
} else {
    foreach ($p in $packages) {
        Write-Host ("Installing {0}..." -f $p.Name) -ForegroundColor Green
        # A non-zero exit is normal when the package is already installed, so this is not
        # treated as fatal. doctor.py is the authority on whether the tool is really there.
        winget install --id $p.Id --accept-package-agreements --accept-source-agreements `
            --disable-interactivity --silent 2>&1 | Out-Null
    }
    if (-not $IncludeOptional) {
        Write-Host 'Skipped optional tools (tesseract, rclone, node). Re-run with -IncludeOptional to add them.' -ForegroundColor DarkGray
    }
    Update-PathFromRegistry
}

# ---- 2. python venv ---------------------------------------------------------
Write-Host ''
Write-Host 'Setting up the Python environment...' -ForegroundColor Green

function Get-RealPython {
    <#
      Returns a working python.exe, or $null.

      Windows 11 ships a FAKE `python` in WindowsApps: a stub that opens the Microsoft
      Store instead of running anything. Get-Command finds it and Test-Path says it
      exists, so a naive check passes and then `python -m venv` silently does nothing.
      The only reliable test is to execute it and see if real Python answers.
    #>
    foreach ($cand in @('python', 'python3', 'py')) {
        $cmd = Get-Command $cand -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        if ($cmd.Source -like '*WindowsApps*') { continue }   # the Store stub
        try {
            $v = & $cmd.Source -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $v) { return $v.Trim() }
        } catch { }
    }
    return $null
}

$python = Get-RealPython
if (-not $python) {
    if ($SkipWinget -or -not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host '!! Python not found. Install it:  winget install --id Python.Python.3.12' -ForegroundColor Red
        exit 1
    }
    Write-Host 'Installing Python (not present on a fresh Windows)...' -ForegroundColor Green
    winget install --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements `
        --disable-interactivity --silent 2>&1 | Out-Null
    Update-PathFromRegistry
    $python = Get-RealPython
    if (-not $python) {
        Write-Host '!! Python installed but not on PATH yet. Close this window, open a NEW' -ForegroundColor Red
        Write-Host '   PowerShell, and re-run setup.' -ForegroundColor Red
        exit 1
    }
}
Write-Host "Using Python: $python" -ForegroundColor DarkGray

$venvPy = Join-Path $plug '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
    & $python -m venv (Join-Path $plug '.venv')
}
if (-not (Test-Path $venvPy)) {
    Write-Host '!! Failed to create the virtual environment.' -ForegroundColor Red
    exit 1
}
Write-Host 'Installing Python packages (this takes a few minutes on first run)...' -ForegroundColor Green
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $plug 'requirements.txt') --quiet

# ---- 3. UTF-8 ---------------------------------------------------------------
# Windows Python defaults stdout to cp1252, which cannot encode the arrows and check marks
# this codebase prints in 82 files. Printing one raises UnicodeEncodeError and kills the
# script mid-pipeline. This makes UTF-8 the default for every future Python process.
if ($env:PYTHONUTF8 -ne '1') {
    [Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
    $env:PYTHONUTF8 = '1'
    Write-Host 'Set PYTHONUTF8=1 (without it, console output can crash scripts).' -ForegroundColor Green
}

# ---- 4. health check --------------------------------------------------------
Write-Host ''
Write-Host 'Running health check...' -ForegroundColor Green
& $venvPy (Join-Path $plug 'doctor.py')
$doctor = $LASTEXITCODE

Write-Host ''
if ($doctor -ne 0) {
    Write-Host 'Setup incomplete. Follow the install lines above, then re-run .\setup.ps1' -ForegroundColor Yellow
} else {
    Write-Host 'Next steps:' -ForegroundColor Cyan
    Write-Host '  1) (optional) paste a free Groq key into plugins\vibe-editing\config\keys.env'
    Write-Host '  2) In Claude Code:  /edit <your youtube link>'
    Write-Host '     or from the terminal:  .\bin\vibe-editing.ps1 "<your youtube link>"'
}
exit $doctor
