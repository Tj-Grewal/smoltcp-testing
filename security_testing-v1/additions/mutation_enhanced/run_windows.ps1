$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")
$PythonCmd = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonCmd)) {
    $PythonCmd = "python"
    if (-not (Get-Command $PythonCmd -ErrorAction SilentlyContinue)) {
        $PythonCmd = "py"
    }
}

& $PythonCmd (Join-Path $ScriptDir "scripts\mutation_runner.py") --platform windows |
    Tee-Object -FilePath (Join-Path $LogDir "mutation_stdout_windows.log")
