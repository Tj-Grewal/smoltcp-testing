$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Push-Location (Join-Path $ScriptDir "conformance_suite")
try {
    cargo test | Tee-Object -FilePath (Join-Path $LogDir "conformance_windows.log")
} finally {
    Pop-Location
}
