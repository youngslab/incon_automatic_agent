
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$gitRoot = git rev-parse --show-toplevel 2>$null

if ($gitRoot) {
    Write-Output "Git repository found at: $gitRoot"
    Set-Location $gitRoot
} else {
    Write-Output "Error: This script must be run inside a Git repository."
    exit 1
}

Write-Output "Updating git repository..."
git pull

$venvPath = "$gitRoot\env"
if (!(Test-Path $venvPath)) {
    Write-Output "Creating virtual environment..."
    python -m venv $venvPath
}

# 3. 가상 환경 활성화
Write-Output "Activating virtual environment..."
& "$venvPath\Scripts\Activate"

# 4. Python 의존성 설치
if (Test-Path "$gitRoot\requirements.txt") {
    Write-Output "Installing dependencies..."
    pip install -r "$gitRoot\requirements.txt"
} else {
    Write-Output "No requirements.txt found."
}

# 5. agent.py 실행
$agentPath = "$gitRoot\agent.py"
if (Test-Path $agentPath) {
    Write-Output "Running agent.py..."
    python $agentPath
} else {
    Write-Output "Error: agent.py not found."
}