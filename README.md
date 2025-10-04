# DocuAI V1 (discontinued)

**AI-powered code documentation generator that automatically detects undocumented functions/classes and creates pull requests with generated documentation.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

- 🔍 **Smart Detection**: Automatically finds undocumented functions and classes
- 🤖 **AI-Powered**: Uses free AI models to generate accurate, contextual comments
- 🔄 **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, C, Go, Rust
- 📝 **Auto PR Creation**: Generates pull requests with documentation changes
- 🎯 **Configurable**: Customizable comment styles and AI models
- 🚀 **Easy Setup**: Simple installation and configuration

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/docuai.git
cd docuai

# Install dependencies
pip install -r requirements.txt

# Install DocuAI
pip install -e .
```

### Basic Usage

```bash
# Analyze your codebase (dry run)
docuai analyze --dry-run

# Generate documentation and create PR
docuai generate

# Test with sample code
docuai test
```

## 📋 Prerequisites

- Python 3.8+
- Git repository with GitHub remote
- GitHub token (for PR creation)

## ⚙️ Configuration

### Environment Variables

```bash
# Required for PR creation
export GITHUB_TOKEN="your_github_token_here"
```

### Configuration File (`config.yaml`)

```yaml
ai:
  model_name: "microsoft/DialoGPT-medium"  # Free model
  max_tokens: 150
  temperature: 0.7
  use_local_model: true

github:
  token_env: "GITHUB_TOKEN"
  base_branch: "main"
  pr_title_prefix: "docs: Auto-generate documentation for"

code_analysis:
  supported_languages:
    - python
    - javascript
    - typescript
    - java
    - cpp
    - c
    - go
    - rust
  
  ignore_patterns:
    - "**/node_modules/**"
    - "**/venv/**"
    - "**/__pycache__/**"
```

## 🎯 Supported Languages

| Language | File Extensions | Comment Style |
|----------|----------------|---------------|
| Python | `.py` | Docstrings (`"""`) |
| JavaScript | `.js`, `.jsx` | JSDoc (`/** */`) |
| TypeScript | `.ts`, `.tsx` | JSDoc (`/** */`) |
| Java | `.java` | JavaDoc (`/** */`) |
| C++ | `.cpp`, `.cc`, `.cxx` | JavaDoc (`/** */`) |
| C | `.c` | JavaDoc (`/** */`) |
| Go | `.go` | Go comments (`//`) |
| Rust | `.rs` | Rust docs (`///`) |

## 🔧 Command Line Interface

### Analyze Command
```bash
# Analyze current directory
docuai analyze

# Analyze specific directory
docuai analyze --directory /path/to/code

# Dry run (show what would change)
docuai analyze --dry-run

# Use custom config
docuai analyze --config custom_config.yaml
```

### Generate Command
```bash
# Generate docs and create PR
docuai generate

# Generate without creating PR
docuai generate --no-pr

# Use custom directory and config
docuai generate --directory /path/to/code --config custom.yaml
```

### Setup Command
```bash
# Check dependencies and configuration
docuai setup
```

### Test Command
```bash
# Test with sample code
docuai test
```

## 🤖 AI Models

DocuAI uses free, open-source models by default:

- **Primary**: Microsoft DialoGPT-medium (free, lightweight)
- **Fallback**: Rule-based comment generation
- **Customizable**: Easy to switch to other models

### Using Different Models

Edit `config.yaml`:
```yaml
ai:
  model_name: "microsoft/DialoGPT-medium"  # Change this
  use_local_model: true  # Set to false for API-based models
```

## 📝 Example Output

### Before (Undocumented Code)
```python
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class DataProcessor:
    def __init__(self, config):
        self.config = config
```

### After (With Generated Documentation)
```python
def calculate_fibonacci(n):
    """
    Calculate the nth Fibonacci number using recursion.
    
    Args:
        n (int): The position in the Fibonacci sequence
    
    Returns:
        int: The nth Fibonacci number
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class DataProcessor:
    """
    DataProcessor class for processing data with configuration.
    
    TODO: Add class description
    """
    def __init__(self, config):
        self.config = config
```

## 🔄 Workflow

1. **Analysis**: Scans codebase for undocumented functions/classes
2. **AI Generation**: Uses AI to generate contextual comments
3. **File Modification**: Applies comments to source files
4. **Git Integration**: Creates branch and commits changes
5. **PR Creation**: Opens pull request with documentation changes

## 🛠️ Development

### Project Structure
```
docuai/
├── core/
│   ├── analyzer.py          # Code analysis
│   ├── ai_generator.py      # AI comment generation
│   ├── github_integration.py # GitHub PR creation
│   └── orchestrator.py      # Main workflow
├── cli.py                   # Command-line interface
├── __init__.py
├── config.yaml             # Configuration
└── requirements.txt        # Dependencies
```

### Adding New Languages

1. Add language to `config.yaml`:
```yaml
code_analysis:
  supported_languages:
    - your_language
  comment_patterns:
    your_language: ["//", "/*", "*"]
```

2. Update file extension mapping in `analyzer.py`
3. Add comment generation logic in `ai_generator.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tree-sitter](https://tree-sitter.github.io/) for code parsing
- [Transformers](https://huggingface.co/transformers/) for AI models
- [Rich](https://rich.readthedocs.io/) for beautiful CLI output
- [PyGithub](https://pygithub.readthedocs.io/) for GitHub integration

## 📞 Support

- 📧 Email: support@docuai.dev
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/docuai/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/docuai/wiki)

---

**Made with ❤️ by the DocuAI Team**
