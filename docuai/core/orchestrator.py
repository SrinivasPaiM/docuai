"""
Main orchestrator module that coordinates all DocuAI components.
"""

import os
import sys
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from .analyzer import CodeAnalyzer
from .ai_generator import AICommentGenerator
from .github_integration import GitHubIntegration


class DocuAIOrchestrator:
    """Main orchestrator for DocuAI workflow."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the orchestrator with all components."""
        self.console = Console()
        self.config_path = config_path
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.analyzer = CodeAnalyzer(config_path)
        self.ai_generator = AICommentGenerator(config_path)
        self.github_integration = None
        
        # Check if GitHub integration is available
        if os.getenv(self.config['github']['token_env']):
            try:
                self.github_integration = GitHubIntegration(config_path)
            except Exception as e:
                self.console.print(f"[yellow]Warning: GitHub integration not available: {e}[/yellow]")
        else:
            self.console.print("[yellow]Warning: GitHub token not found. PR creation will be disabled.[/yellow]")
    
    def analyze_codebase(self, directory: str = ".") -> Dict[str, List[Dict]]:
        """Analyze the codebase for undocumented functions and classes."""
        self.console.print(f"[blue]Analyzing codebase in: {directory}[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Scanning files...", total=None)
            
            results = self.analyzer.analyze_directory(directory)
            
            progress.update(task, description="Analysis complete!")
        
        return results
    
    def generate_comments(self, analysis_results: Dict[str, List[Dict]]) -> Dict[str, Dict[str, str]]:
        """Generate comments for all undocumented functions and classes."""
        self.console.print("[blue]Generating AI comments...[/blue]")
        
        all_comments = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating comments...", total=len(analysis_results))
            
            for file_path, functions in analysis_results.items():
                if functions:
                    language = self._get_language_from_file(file_path)
                    file_comments = {}
                    
                    for func_info in functions:
                        comment = self.ai_generator.generate_comment(func_info, language)
                        file_comments[func_info['name']] = comment
                    
                    all_comments[file_path] = file_comments
                
                progress.advance(task)
        
        return all_comments
    
    def _get_language_from_file(self, file_path: str) -> str:
        """Get language from file extension."""
        ext = Path(file_path).suffix.lower()
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
        }
        return ext_to_lang.get(ext, 'python')
    
    def create_pull_request(self, analysis_results: Dict[str, List[Dict]], comments: Dict[str, Dict[str, str]]) -> Optional[str]:
        """Create a pull request with the generated documentation."""
        if not self.github_integration:
            self.console.print("[red]GitHub integration not available. Cannot create pull request.[/red]")
            return None
        
        self.console.print("[blue]Creating pull request...[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Creating PR...", total=None)
            
            pr_url = self.github_integration.create_documentation_pr(analysis_results, comments)
            
            progress.update(task, description="PR creation complete!")
        
        return pr_url
    
    def run_dry_run(self, directory: str = ".") -> str:
        """Run a dry run to show what would be changed."""
        self.console.print("[blue]Running dry run analysis...[/blue]")
        
        # Analyze codebase
        analysis_results = self.analyze_codebase(directory)
        
        if not analysis_results:
            return "No undocumented functions or classes found."
        
        # Generate comments
        comments = self.generate_comments(analysis_results)
        
        # Create summary
        if self.github_integration:
            summary = self.github_integration.create_dry_run_summary(analysis_results, comments)
        else:
            summary = self._create_simple_summary(analysis_results, comments)
        
        return summary
    
    def _create_simple_summary(self, analysis_results: Dict[str, List[Dict]], comments: Dict[str, Dict[str, str]]) -> str:
        """Create a simple summary without GitHub integration."""
        summary = ["DocuAI Analysis Summary", "=" * 50, ""]
        
        total_functions = 0
        total_files = 0
        
        for file_path, functions in analysis_results.items():
            if file_path in comments:
                file_comments = comments[file_path]
                documented_functions = [f for f in functions if f['name'] in file_comments]
                
                if documented_functions:
                    total_files += 1
                    total_functions += len(documented_functions)
                    
                    summary.append(f"📁 {file_path}")
                    for func_info in documented_functions:
                        func_name = func_info['name']
                        func_type = func_info['type']
                        summary.append(f"  - {func_type}: {func_name}")
                    summary.append("")
        
        summary.extend([
            f"Total files to modify: {total_files}",
            f"Total functions/classes to document: {total_functions}",
        ])
        
        return '\n'.join(summary)
    
    def run_full_workflow(self, directory: str = ".", create_pr: bool = True) -> Optional[str]:
        """Run the complete DocuAI workflow."""
        self.console.print(Panel.fit(
            "[bold blue]DocuAI - AI-Powered Code Documentation Generator[/bold blue]\n"
            "🤖 Automatically detecting and documenting your code",
            border_style="blue"
        ))
        
        # Step 1: Analyze codebase
        analysis_results = self.analyze_codebase(directory)
        
        if not analysis_results:
            self.console.print("[green]✅ No undocumented functions or classes found![/green]")
            return None
        
        # Display analysis results
        self._display_analysis_results(analysis_results)
        
        # Step 2: Generate comments
        comments = self.generate_comments(analysis_results)
        
        # Step 3: Create pull request or show dry run
        if create_pr and self.github_integration:
            pr_url = self.create_pull_request(analysis_results, comments)
            if pr_url:
                self.console.print(f"[green]✅ Pull request created: {pr_url}[/green]")
                return pr_url
            else:
                self.console.print("[red]❌ Failed to create pull request[/red]")
                return None
        else:
            # Show dry run summary
            summary = self.run_dry_run(directory)
            self.console.print(Panel(summary, title="Dry Run Summary", border_style="yellow"))
            return None
    
    def _display_analysis_results(self, analysis_results: Dict[str, List[Dict]]):
        """Display analysis results in a formatted table."""
        table = Table(title="Undocumented Functions and Classes Found")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Name", style="green")
        table.add_column("Line", style="yellow")
        
        for file_path, functions in analysis_results.items():
            for func_info in functions:
                table.add_row(
                    file_path,
                    func_info['type'],
                    func_info['name'],
                    str(func_info['line'])
                )
        
        self.console.print(table)
