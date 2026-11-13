$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $PythonLauncher) {
    throw 'Python Launcher (py.exe) was not found. Install/enable the Windows Python Launcher; this script will not alter your existing Python installations.'
}

# Do not probe versions that are not installed: under Windows PowerShell 5.1,
# a failed py -3.11 probe can become a terminating NativeCommandError even
# when stderr is redirected. Read the launcher's installed-runtime list first.
$LauncherOutput = @(& py -0p)
$LauncherExitCode = $LASTEXITCODE
if ($LauncherExitCode -ne 0) {
    throw 'Could not enumerate installed Python runtimes with py -0p. Run py -0p manually and share its output.'
}

$AvailableVersions = @()
foreach ($Line in $LauncherOutput) {
    $LineText = [string]$Line
    if ($LineText -match '^\s*-V:(?<Version>3\.(?:11|12))(?=\s|$)') {
        $AvailableVersions += $Matches['Version']
    } elseif ($LineText -match '^\s*-(?<Version>3\.(?:11|12))(?:-64)?(?=\s|$)') {
        # Also accept the legacy py -0 output format.
        $AvailableVersions += $Matches['Version']
    }
}

# Prefer 3.12, then 3.11. Only select versions the launcher actually listed.
$SelectedPython = $null
foreach ($PreferredVersion in @('3.12', '3.11')) {
    if ($AvailableVersions -contains $PreferredVersion) {
        $SelectedPython = $PreferredVersion
        break
    }
}
if (-not $SelectedPython) {
    throw 'A 64-bit Python 3.11 or 3.12 installation was not found in py -0p. Your Python 3.12 installation should appear as -V:3.12 in that list.'
}

# Verify the selected interpreter is 64-bit before creating the environment.
$ProbeOutput = @(& py ("-" + $SelectedPython) -c "import struct,sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor)+'|'+str(struct.calcsize('P')*8))")
$ProbeExitCode = $LASTEXITCODE
$Probe = ($ProbeOutput -join '').Trim()
if ($ProbeExitCode -ne 0 -or $Probe -ne ($SelectedPython + '|64')) {
    throw "Python $SelectedPython was listed by py -0p but failed the 64-bit runtime check. Probe output: $Probe"
}

Write-Host "Using 64-bit Python $SelectedPython" -ForegroundColor Cyan
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path $VenvPython)) {
    & py ("-" + $SelectedPython) -m venv (Join-Path $Root '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}

# Never silently use a 32-bit or unsupported pre-existing virtual environment.
$VenvProbeOutput = @(& $VenvPython -c "import struct,sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor)+'|'+str(struct.calcsize('P')*8))")
$VenvProbeExitCode = $LASTEXITCODE
$VenvProbe = ($VenvProbeOutput -join '').Trim()
if ($VenvProbeExitCode -ne 0 -or $VenvProbe -notmatch '^3\.(11|12)\|64$') {
    throw 'The existing .venv is not 64-bit Python 3.11/3.12. Remove only this project .venv folder and run setup again.'
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $VenvPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Installed package dependency checks failed.' }

# Catch missing native DLLs before downloading a multi-hundred-MB model.
& $VenvPython -c "import av, ctranslate2, faster_whisper, huggingface_hub, onnxruntime, psutil, rapidfuzz, tokenizers; print('Native runtime imports: OK')"
if ($LASTEXITCODE -ne 0) { throw 'A native runtime import failed. Check Python x64 and install the latest Microsoft Visual C++ v14 x64 Redistributable if the error mentions a missing DLL; then rerun setup.' }
& $VenvPython -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Scroll up and share the failure output.' }

Write-Host ''
Write-Host 'Verification setup complete.' -ForegroundColor Green
Write-Host 'Next: put a 30-120 second audio clip under .\audio and run .\scripts\run-small.ps1 -Audio .\audio\sample.wav'
