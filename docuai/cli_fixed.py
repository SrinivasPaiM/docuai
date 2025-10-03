"""
Fixed CLI for DocuAI that falls back to simple components when AI model fails.
"""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Try to import the main orchestrator, fall back to simple components
try:
    from .core.orchestrator import DocuAIOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except Exception as e:
    print(f"Warning: Main orchestrator not available: {e}")
    ORCHESTRATOR_AVAILABLE = False

# Import simple components as fallback
from .core.simple_analyzer import SimpleAnalyzer
from .core.simple_generator import SimpleGenerator


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
        if ORCHESTRATOR_AVAILABLE:
            orchestrator = DocuAIOrchestrator(config)
            if dry_run:
                console.print("[blue]Running dry run analysis...[/blue]")
                summary = orchestrator.run_dry_run(directory)
                console.print(Panel(summary, title="Dry Run Results", border_style="yellow"))
            else:
                console.print("[blue]Running full analysis...[/blue]")
                orchestrator.run_full_workflow(directory, create_pr=False)
        else:
            # Use simple components
            console.print("[blue]Using simple analyzer (AI model not available)...[/blue]")
            analyzer = SimpleAnalyzer()
            results = analyzer.analyze_directory(directory)
            
            if not results:
                console.print("[green]✅ No undocumented functions or classes found![/green]")
                return
            
            # Display results
            console.print(f"[blue]Found undocumented functions/classes in {len(results)} files:[/blue]")
            for file_path, functions in results.items():
                console.print(f"\n📁 {file_path}")
                for func_info in functions:
                    console.print(f"  - {func_info['name']} ({func_info['type']}) at line {func_info['line']}")
            
            if not dry_run:
                # Generate comments
                console.print("\n[blue]Generating comments...[/blue]")
                generator = SimpleGenerator()
                
                for file_path, functions in results.items():
                    language = analyzer._get_language_from_extension(file_path)
                    if language:
                        for func_info in functions:
                            comment = generator.generate_comment(func_info, language)
                            console.print(f"\n{func_info['name']} ({func_info['type']}):")
                            console.print(comment)
            
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
        if ORCHESTRATOR_AVAILABLE:
            orchestrator = DocuAIOrchestrator(config)
            create_pr = not no_pr
            pr_url = orchestrator.run_full_workflow(directory, create_pr=create_pr)
            
            if pr_url:
                console.print(f"[green]✅ Success! Pull request created: {pr_url}[/green]")
            elif not create_pr:
                console.print("[green]✅ Documentation generation completed![/green]")
            else:
                console.print("[yellow]⚠️  No changes were made or PR creation failed.[/yellow]")
        else:
            # Use simple components
            console.print("[blue]Using simple components (AI model not available)...[/blue]")
            analyzer = SimpleAnalyzer()
            results = analyzer.analyze_directory(directory)
            
            if not results:
                console.print("[green]✅ No undocumented functions or classes found![/green]")
                return
            
            console.print(f"[blue]Found undocumented functions/classes in {len(results)} files[/blue]")
            
            # Generate comments
            generator = SimpleGenerator()
            for file_path, functions in results.items():
                language = analyzer._get_language_from_extension(file_path)
                if language:
                    console.print(f"\n📁 {file_path}")
                    for func_info in functions:
                        comment = generator.generate_comment(func_info, language)
                        console.print(f"\n{func_info['name']} ({func_info['type']}):")
                        console.print(comment)
            
            console.print("\n[yellow]⚠️  Simple mode: Comments generated but not applied to files.[/yellow]")
            console.print("To apply comments, you'll need to install AI dependencies or use the main orchestrator.")
            
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
        console.print("[green]✅ Full DocuAI functionality available[/green]")
    except ImportError as e:
        console.print(f"[yellow]⚠️  AI dependencies not available: {e}[/yellow]")
        console.print("[blue]ℹ️  Using simple mode (rule-based comment generation)[/blue]")
        console.print("Run: pip install torch transformers for full AI functionality")
    
    # Check tree-sitter dependencies
    try:
        import tree_sitter
        console.print("[green]✅ Tree-sitter available[/green]")
    except ImportError as e:
        console.print(f"[yellow]⚠️  Tree-sitter not available: {e}[/yellow]")
        console.print("[blue]ℹ️  Using simple regex-based analysis[/blue]")
    
    console.print("\n[green]Setup complete![/green]")
    console.print("Run 'docuai analyze' to start analyzing your code.")


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
        return self._transform_data(data)
    
    def _transform_data(self, data):
        return [item * 2 for item in data if isinstance(item, (int, float))]
'''
    
    test_file = Path("test_sample.py")
    test_file.write_text(test_content)
    
    try:
        if ORCHESTRATOR_AVAILABLE:
            orchestrator = DocuAIOrchestrator(config)
            console.print("[blue]Running test analysis...[/blue]")
            
            # Run dry run on test file
            summary = orchestrator.run_dry_run(".")
            console.print(Panel(summary, title="Test Results", border_style="green"))
        else:
            # Use simple components
            console.print("[blue]Using simple components for test...[/blue]")
            analyzer = SimpleAnalyzer()
            results = analyzer.analyze_file("test_sample.py")
            
            if results:
                console.print(f"[green]✅ Found {len(results)} undocumented functions/classes:[/green]")
                generator = SimpleGenerator()
                
                for func_info in results:
                    comment = generator.generate_comment(func_info, 'python')
                    console.print(f"\n{func_info['name']} ({func_info['type']}):")
                    console.print(comment)
            else:
                console.print("[yellow]No undocumented functions found in test file.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            console.print("[blue]Cleaned up test file[/blue]")


if __name__ == '__main__':
    cli()
