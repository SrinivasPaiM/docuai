#!/bin/bash

# DocuAI Installation Script
# This script installs DocuAI and its dependencies

set -e

echo "🤖 DocuAI Installation Script"
echo "=============================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using one:"
    echo "   python3 -m venv docuai-env"
    echo "   source docuai-env/bin/activate"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install DocuAI in development mode
echo "Installing DocuAI..."
pip install -e .

# Check if git is available
if command -v git &> /dev/null; then
    echo "✅ Git is available"
else
    echo "⚠️  Git is not available. GitHub integration will not work."
fi

# Check for GitHub token
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GitHub token found"
else
    echo "⚠️  GitHub token not found. Set GITHUB_TOKEN environment variable for PR creation."
    echo "   Get your token from: https://github.com/settings/tokens"
fi

# Test installation
echo "Testing installation..."
if docuai --version &> /dev/null; then
    echo "✅ DocuAI installed successfully!"
    echo ""
    echo "🚀 Quick start:"
    echo "   docuai setup          # Check configuration"
    echo "   docuai test           # Test with sample code"
    echo "   docuai analyze --dry-run  # Analyze your codebase"
    echo ""
    echo "📖 For more information, see README.md"
else
    echo "❌ Installation test failed"
    exit 1
fi
