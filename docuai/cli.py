"""
Command-line interface for DocuAI.
"""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .core.orchestrator import DocuAIOrchestrator


@click.group()
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """DocuAI - AI-powered code documentation generator."""
    ctx.ensure_object(dict)
    ctx.obj['console'] = Console()


@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to analyze')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without making changes')
def analyze(directory, config, dry_run):
    """Analyze codebase for undocumented functions and classes."""
    console = Console()
    
    try:
        orchestrator = DocuAIOrchestrator(config)
        
        if dry_run:
            console.print("[blue]Running dry run analysis...[/blue]")
            summary = orchestrator.run_dry_run(directory)
            console.print(Panel(summary, title="Dry Run Results", border_style="yellow"))
        else:
            console.print("[blue]Running full analysis...[/blue]")
            orchestrator.run_full_workflow(directory, create_pr=False)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to analyze')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--no-pr', is_flag=True, help='Skip creating pull request')
def generate(directory, config, no_pr):
    """Generate documentation and create pull request."""
    console = Console()
    
    try:
        orchestrator = DocuAIOrchestrator(config)
        
        create_pr = not no_pr
        pr_url = orchestrator.run_full_workflow(directory, create_pr=create_pr)
        
        if pr_url:
            console.print(f"[green]✅ Success! Pull request created: {pr_url}[/green]")
        elif not create_pr:
            console.print("[green]✅ Documentation generation completed![/green]")
        else:
            console.print("[yellow]⚠️  No changes were made or PR creation failed.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def setup(config):
    """Setup DocuAI configuration and check dependencies."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]DocuAI Setup[/bold blue]\n"
        "Setting up configuration and checking dependencies...",
        border_style="blue"
    ))
    
    # Check if config file exists
    if not Path(config).exists():
        console.print(f"[yellow]Configuration file {config} not found. Using defaults.[/yellow]")
    
    # Check GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        console.print("[green]✅ GitHub token found[/green]")
    else:
        console.print("[yellow]⚠️  GitHub token not found. Set GITHUB_TOKEN environment variable for PR creation.[/yellow]")
    
    # Check Python dependencies
    try:
        import torch
        import transformers
        console.print("[green]✅ AI dependencies available[/green]")
    except ImportError as e:
        console.print(f"[red]❌ Missing AI dependencies: {e}[/red]")
        console.print("Run: pip install -r requirements.txt")
    
    # Check tree-sitter dependencies
    try:
        import tree_sitter
        console.print("[green]✅ Tree-sitter available[/green]")
    except ImportError as e:
        console.print(f"[yellow]⚠️  Tree-sitter not available: {e}[/yellow]")
        console.print("Some language features may not work optimally.")
    
    console.print("\n[green]Setup complete![/green]")
    console.print("Run 'docuai generate' to start generating documentation.")


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def test(config):
    """Test DocuAI with a sample file."""
    console = Console()
    
    console.print("[blue]Creating test file...[/blue]")
    
    # Create a test Python file with undocumented functions
    test_content = '''def calculate_sum(a, b):
    return a + b

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, data):
        return self.process_data(data)
'''
    
    test_file = Path("test_sample.py")
    test_file.write_text(test_content)
    
    try:
        orchestrator = DocuAIOrchestrator(config)
        console.print("[blue]Running test analysis...[/blue]")
        
        # Run dry run on test file
        summary = orchestrator.run_dry_run(".")
        console.print(Panel(summary, title="Test Results", border_style="green"))
        
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            console.print("[blue]Cleaned up test file[/blue]")


if __name__ == '__main__':
    cli()
