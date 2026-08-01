# OMNI-Agent-OS Claude Desktop Installer
# This script injects the OMNI MCP Server into Claude Desktop's configuration.

$ErrorActionPreference = "Stop"

Write-Host "========================================="
Write-Host " OMNI-Agent-OS Claude Desktop Installer"
Write-Host "========================================="

$ClaudeConfigDir = Join-Path $env:APPDATA "Claude"
$ClaudeConfigFile = Join-Path $ClaudeConfigDir "claude_desktop_config.json"
$OmniScriptPath = "C:\AI\Projects\AI-Agent-OS\src\mcp\omni_server.py"

# Verify python exists
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ClaudeConfigDir)) {
    Write-Host "Claude config directory not found. Creating..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $ClaudeConfigDir | Out-Null
}

$ConfigData = @{}
if (Test-Path $ClaudeConfigFile) {
    Write-Host "Found existing Claude configuration."
    try {
        $ConfigContent = Get-Content $ClaudeConfigFile -Raw
        if ($ConfigContent.Trim() -ne "") {
            $ConfigData = $ConfigContent | ConvertFrom-Json -AsHashtable
        }
    } catch {
        Write-Host "Failed to parse existing config. Creating new..." -ForegroundColor Yellow
    }
}

if (-not $ConfigData.ContainsKey("mcpServers")) {
    $ConfigData["mcpServers"] = @{}
}

$OmniServerConfig = @{
    command = "python"
    args = @($OmniScriptPath)
}

$ConfigData["mcpServers"]["omni-agent-os"] = $OmniServerConfig

$JsonConfig = $ConfigData | ConvertTo-Json -Depth 10

Set-Content -Path $ClaudeConfigFile -Value $JsonConfig -Encoding UTF8

Write-Host "Successfully installed OMNI-Agent-OS as an MCP Server!" -ForegroundColor Green
Write-Host "Please restart Claude Desktop to apply changes." -ForegroundColor Cyan
