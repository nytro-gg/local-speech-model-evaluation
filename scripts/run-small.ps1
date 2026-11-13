param(
    [Parameter(Mandatory=$true)][string]$Audio,
    [string]$Reference = ''
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$OriginalLocation = Get-Location

# Resolve relative paths against the folder from which the user invoked the script,
# before changing directory to the project root.
if ([System.IO.Path]::IsPathRooted($Audio)) {
    $AudioCandidate = $Audio
} else {
    $AudioCandidate = Join-Path $OriginalLocation $Audio
}
if (-not (Test-Path -LiteralPath $AudioCandidate -PathType Leaf)) {
    throw "Audio file not found: $AudioCandidate"
}
$AudioAbsolute = (Resolve-Path -LiteralPath $AudioCandidate).Path

$ReferenceArgs = @()
if ($Reference -ne '') {
    if ([System.IO.Path]::IsPathRooted($Reference)) {
        $ReferenceCandidate = $Reference
    } else {
        $ReferenceCandidate = Join-Path $OriginalLocation $Reference
    }
    if (-not (Test-Path -LiteralPath $ReferenceCandidate -PathType Leaf)) {
        throw "Reference transcript not found: $ReferenceCandidate"
    }
    $ReferenceAbsolute = (Resolve-Path -LiteralPath $ReferenceCandidate).Path
    $ReferenceArgs = @('--reference', $ReferenceAbsolute)
}

Set-Location $Root
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'Environment missing. Run .\scripts\setup.ps1 first.' }
& $Python -m src.evaluate --audio $AudioAbsolute --model small --device cpu --compute-type int8 --max-audio-seconds 120 @ReferenceArgs
if ($LASTEXITCODE -ne 0) { throw 'Evaluation failed. See the error printed above.' }
