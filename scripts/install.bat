@echo off
REM DocuAI Installation Script for Windows
REM This script installs DocuAI and its dependencies

echo 🤖 DocuAI Installation Script
echo ==============================

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is available

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment detected: %VIRTUAL_ENV%
) else (
    echo ⚠️  No virtual environment detected. Consider using one:
    echo    python -m venv docuai-env
    echo    docuai-env\Scripts\activate
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install DocuAI in development mode
echo Installing DocuAI...
pip install -e .

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git is not available. GitHub integration will not work.
) else (
    echo ✅ Git is available
)

REM Check for GitHub token
if defined GITHUB_TOKEN (
    echo ✅ GitHub token found
) else (
    echo ⚠️  GitHub token not found. Set GITHUB_TOKEN environment variable for PR creation.
    echo    Get your token from: https://github.com/settings/tokens
)

REM Test installation
echo Testing installation...
docuai --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Installation test failed
    pause
    exit /b 1
) else (
    echo ✅ DocuAI installed successfully!
    echo.
    echo 🚀 Quick start:
    echo    docuai setup          # Check configuration
    echo    docuai test           # Test with sample code
    echo    docuai analyze --dry-run  # Analyze your codebase
    echo.
    echo 📖 For more information, see README.md
)

pause
