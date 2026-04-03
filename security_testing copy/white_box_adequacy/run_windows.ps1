$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogPath = Join-Path $LogDir "llvm_cov_windows.log"

rustup component add llvm-tools-preview | Out-File -FilePath $LogPath -Append

& cargo llvm-cov --version 2>$null
if ($LASTEXITCODE -ne 0) {
    cargo install cargo-llvm-cov | Out-File -FilePath $LogPath -Append
}

cargo llvm-cov --lib --summary-only 2>&1 | Tee-Object -FilePath $LogPath -Append
