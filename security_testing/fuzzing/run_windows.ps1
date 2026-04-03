$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogPath = Join-Path $LogDir "fuzzing_windows.log"

$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$FuzzDir = Join-Path $RepoRoot "fuzz"

& cargo fuzz --help 2>$null
if ($LASTEXITCODE -ne 0) {
    "Installing cargo-fuzz..." | Tee-Object -FilePath $LogPath -Append
    cargo install cargo-fuzz | Tee-Object -FilePath $LogPath -Append
}

"Ensuring nightly toolchain for sanitizer support..." | Tee-Object -FilePath $LogPath -Append
rustup toolchain install nightly | Tee-Object -FilePath $LogPath -Append

$Targets = @("packet_parser", "tcp_headers", "dhcp_header", "ieee802154_header", "sixlowpan_packet")

Push-Location $FuzzDir
try {
    foreach ($t in $Targets) {
        "=== Fuzz target: $t ===" | Tee-Object -FilePath $LogPath -Append
        $output = cargo +nightly fuzz run -s none $t -- -max_total_time=60 2>&1
        $output | Tee-Object -FilePath $LogPath -Append

        if ($LASTEXITCODE -ne 0) {
            "Target $t exited with failure. Checking artifacts..." | Tee-Object -FilePath $LogPath -Append
            $artifactDir = Join-Path $FuzzDir "artifacts\$t"
            if (Test-Path $artifactDir) {
                Get-ChildItem $artifactDir | ForEach-Object {
                    "Reproducing crash: $($_.FullName)" | Tee-Object -FilePath $LogPath -Append
                    $env:RUST_BACKTRACE = "1"
                    cargo +nightly fuzz run -s none $t $_.FullName 2>&1 | Tee-Object -FilePath $LogPath -Append
                }
            }
        }
    }
} finally {
    Pop-Location
}
