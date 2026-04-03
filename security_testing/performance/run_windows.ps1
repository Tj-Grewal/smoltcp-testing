$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Runs = 5
$LogPath = Join-Path $LogDir "loopback_benchmark_windows.log"
$CsvPath = Join-Path $LogDir "loopback_benchmark_windows.csv"

Push-Location (Join-Path $ScriptDir "loopback_perf_suite")
try {
    $results = @()
    for ($i = 1; $i -le $Runs; $i++) {
        "=== Run $i ===" | Out-File -FilePath $LogPath -Append
        $output = cargo run --release 2>&1
        $output | Out-File -FilePath $LogPath -Append

        $bw = $null
        $secs = $null
        foreach ($line in $output) {
            if ($line -match "duration_s=([0-9\.]+) bandwidth_gbps=([0-9\.]+)") {
                $secs = [double]$matches[1]
                $bw = [double]$matches[2]
            }
        }

        $results += [pscustomobject]@{
            run = $i
            duration_s = $secs
            bandwidth_gbps = $bw
        }
    }

    $results | Export-Csv -Path $CsvPath -NoTypeInformation
} finally {
    Pop-Location
}
