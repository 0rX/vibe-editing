<#
.SYNOPSIS
    Install the script-cut toolchain (Montreal Forced Aligner) to a persistent location.

.DESCRIPTION
    Idempotent: re-running skips anything already present.

    Installs:
      - micromamba             -> $Root\bin\micromamba.exe
      - MFA conda env + models -> $Root\mfa_env  (montreal-forced-aligner + english_us_arpa)
      - python venv            -> $Root\venv     (numpy, num2words, soundfile, matplotlib)

    This is an OPTIONAL toolchain, needed only by the script-cut skill. Everything else in
    the kit works without it.

    NOTE: ASCII-only on purpose. Windows PowerShell 5.1 reads a BOM-less UTF-8 script as
    ANSI, so any dash or arrow here would render as mojibake.

.EXAMPLE
    .\setup_toolchain.ps1
    .\setup_toolchain.ps1 -Root D:\mfa
#>
[CmdletBinding()]
param(
    [string]$Root = (Join-Path $env:LOCALAPPDATA 'vibe-editing\script-cut')
)

$ErrorActionPreference = 'Stop'
if ($env:SCRIPT_CUT_ROOT) { $Root = $env:SCRIPT_CUT_ROOT }

New-Item -ItemType Directory -Force -Path (Join-Path $Root 'bin') | Out-Null
Write-Host "==> script-cut toolchain root: $Root" -ForegroundColor Cyan

# ---- 1. micromamba ----------------------------------------------------------
# The bash original picked between osx-arm64 and osx-64 and untarred a bz2. The Windows
# build is a plain .exe, so this just downloads it.
$mamba = Join-Path $Root 'bin\micromamba.exe'
if (-not (Test-Path $mamba)) {
    Write-Host '==> installing micromamba' -ForegroundColor Green
    $url = 'https://micro.mamba.pm/api/micromamba/win-64/latest'
    $tmp = Join-Path $env:TEMP 'micromamba.tar.bz2'
    Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
    # tar.exe ships with Windows 10 1803+ and handles bz2.
    $extract = Join-Path $env:TEMP 'micromamba_x'
    New-Item -ItemType Directory -Force -Path $extract | Out-Null
    & tar.exe -xf $tmp -C $extract
    $found = Get-ChildItem $extract -Recurse -Filter 'micromamba.exe' | Select-Object -First 1
    if (-not $found) { throw 'micromamba.exe not found in the downloaded archive' }
    Copy-Item $found.FullName $mamba -Force
    Remove-Item $tmp, $extract -Recurse -Force -ErrorAction SilentlyContinue
}

# ---- 2. MFA conda env + english_us_arpa models ------------------------------
$mfaEnv = Join-Path $Root 'mfa_env'
if (-not (Test-Path $mfaEnv)) {
    Write-Host '==> creating MFA env (montreal-forced-aligner)' -ForegroundColor Green
    & $mamba create -y -p $mfaEnv -c conda-forge montreal-forced-aligner
}
Write-Host '==> ensuring english_us_arpa acoustic + dictionary models' -ForegroundColor Green
# Model downloads are best-effort: already-present models make these exit non-zero.
& $mamba run -p $mfaEnv mfa model download acoustic   english_us_arpa 2>&1 | Out-Null
& $mamba run -p $mfaEnv mfa model download dictionary english_us_arpa 2>&1 | Out-Null

# ---- 3. python venv (engine + QC deps) --------------------------------------
$venv = Join-Path $Root 'venv'
$venvPy = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
    Write-Host '==> creating python venv' -ForegroundColor Green
    & python -m venv --system-site-packages $venv
}
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install numpy num2words soundfile matplotlib --quiet

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host '!! ffmpeg not found on PATH - install it: winget install --id Gyan.FFmpeg' -ForegroundColor Yellow
}

# ---- 4. how to use it -------------------------------------------------------
Write-Host ''
Write-Host '==> done. Set these for the current session:' -ForegroundColor Cyan
Write-Host "    `$env:MFA_MAMBA = '$mamba'"
Write-Host "    `$env:MFA_ENV   = '$mfaEnv'"
Write-Host ''
Write-Host '    ...or persist them for future sessions:' -ForegroundColor DarkGray
Write-Host "    [Environment]::SetEnvironmentVariable('MFA_MAMBA', '$mamba', 'User')"
Write-Host "    [Environment]::SetEnvironmentVariable('MFA_ENV', '$mfaEnv', 'User')"
Write-Host ''
Write-Host '    Then run the engine with that venv:' -ForegroundColor DarkGray
Write-Host "    & '$venvPy' `"`$env:CLAUDE_PLUGIN_ROOT\skills\script-cut\scripts\script_cut.py`" --source ... --transcript ... --spec ... --out ..."
