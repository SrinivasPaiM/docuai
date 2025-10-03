"""
GitHub integration module for creating pull requests with generated documentation.
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from github import Github, GithubException
from git import Repo, InvalidGitRepositoryError
import yaml
from pathlib import Path


class GitHubIntegration:
    """Handles GitHub integration for creating pull requests."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize GitHub integration with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.github_config = self.config['github']
        self.token_env = self.github_config['token_env']
        self.base_branch = self.github_config['base_branch']
        self.pr_title_prefix = self.github_config['pr_title_prefix']
        self.pr_body_template = self.github_config['pr_body_template']
        
        # Initialize GitHub client
        self.github = None
        self.repo = None
        self._setup_github()
    
    def _setup_github(self):
        """Setup GitHub client and repository."""
        token = os.getenv(self.token_env)
        if not token:
            raise ValueError(f"GitHub token not found in environment variable {self.token_env}")
        
        try:
            self.github = Github(token)
            self.repo = self._get_repository()
        except Exception as e:
            raise ValueError(f"Failed to initialize GitHub client: {e}")
    
    def _get_repository(self):
        """Get the current repository."""
        try:
            # Try to get repo from current directory
            repo = Repo('.')
            remote_url = repo.remotes.origin.url
            
            # Extract owner/repo from URL
            if 'github.com' in remote_url:
                # Handle both HTTPS and SSH URLs
                if remote_url.startswith('https://'):
                    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
                else:  # SSH
                    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
                
                if match:
                    owner, repo_name = match.groups()
                    return self.github.get_repo(f"{owner}/{repo_name}")
            
            raise ValueError("Could not determine repository from git remote")
            
        except InvalidGitRepositoryError:
            raise ValueError("Not in a git repository")
        except Exception as e:
            raise ValueError(f"Failed to get repository: {e}")
    
    def _create_branch_name(self, files_modified: List[str]) -> str:
        """Create a branch name for the documentation PR."""
        # Create a descriptive branch name
        timestamp = str(int(__import__('time').time()))
        return f"docuai-auto-docs-{timestamp}"
    
    def _apply_comment_to_file(self, file_path: str, function_info: Dict, comment: str, language: str) -> bool:
        """Apply generated comment to a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the position to insert the comment
            position = function_info['position']
            line_num = function_info['line']
            
            # Split content into lines
            lines = content.split('\n')
            
            # Insert comment before the function/class
            if language == 'python':
                # For Python, insert docstring right after the definition line
                if function_info['type'] == 'function':
                    # Find the end of the function definition line
                    def_line = lines[line_num - 1]
                    if ':' in def_line:
                        # Insert after the colon
                        indent = len(def_line) - len(def_line.lstrip())
                        comment_lines = [comment]
                        comment_lines[0] = ' ' * (indent + 4) + comment_lines[0]
                        for i in range(1, len(comment_lines)):
                            comment_lines[i] = ' ' * (indent + 4) + comment_lines[i]
                        
                        lines.insert(line_num, '\n'.join(comment_lines))
                    else:
                        lines.insert(line_num, comment)
                else:  # class
                    lines.insert(line_num, comment)
            
            elif language in ['javascript', 'typescript']:
                # For JS/TS, insert JSDoc comment before the function/class
                lines.insert(line_num - 1, comment)
            
            elif language in ['java', 'cpp', 'c']:
                # For Java/C++, insert JavaDoc comment before the function/class
                lines.insert(line_num - 1, comment)
            
            elif language == 'go':
                # For Go, insert comment before the function/struct
                lines.insert(line_num - 1, comment)
            
            elif language == 'rust':
                # For Rust, insert documentation comment before the function/struct
                lines.insert(line_num - 1, comment)
            
            # Write the modified content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return True
            
        except Exception as e:
            print(f"Error applying comment to {file_path}: {e}")
            return False
    
    def _create_commit_message(self, files_modified: List[str], functions_documented: int) -> str:
        """Create a commit message for the documentation changes."""
        return f"docs: Auto-generate documentation for {functions_documented} functions/classes\n\nGenerated by DocuAI 🤖\n\nFiles modified: {', '.join(files_modified)}"
    
    def create_documentation_pr(self, analysis_results: Dict[str, List[Dict]], comments: Dict[str, Dict[str, str]]) -> Optional[str]:
        """Create a pull request with generated documentation."""
        try:
            # Get current repository
            repo = Repo('.')
            
            # Create new branch
            branch_name = self._create_branch_name(list(analysis_results.keys()))
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            # Apply comments to files
            files_modified = []
            functions_documented = 0
            
            for file_path, functions in analysis_results.items():
                if file_path in comments:
                    file_comments = comments[file_path]
                    language = self._get_language_from_file(file_path)
                    
                    for func_info in functions:
                        func_name = func_info['name']
                        if func_name in file_comments:
                            comment = file_comments[func_name]
                            if self._apply_comment_to_file(file_path, func_info, comment, language):
                                functions_documented += 1
                                if file_path not in files_modified:
                                    files_modified.append(file_path)
            
            if not files_modified:
                print("No files were modified. Skipping PR creation.")
                return None
            
            # Commit changes
            repo.git.add('.')
            commit_message = self._create_commit_message(files_modified, functions_documented)
            repo.index.commit(commit_message)
            
            # Push branch
            origin = repo.remotes.origin
            origin.push(new_branch)
            
            # Create pull request
            pr_title = f"{self.pr_title_prefix} {functions_documented} functions/classes"
            pr_body = self.pr_body_template.format(
                files_modified='\n'.join(f"- {f}" for f in files_modified)
            )
            
            pr = self.repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=self.base_branch
            )
            
            print(f"Created pull request: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            print(f"Error creating pull request: {e}")
            return None
    
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
    
    def create_dry_run_summary(self, analysis_results: Dict[str, List[Dict]], comments: Dict[str, Dict[str, str]]) -> str:
        """Create a summary of what would be changed in dry run mode."""
        summary = ["DocuAI Dry Run Summary", "=" * 50, ""]
        
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
            "",
            "Generated comments preview:",
            "-" * 30
        ])
        
        # Show sample comments
        sample_count = 0
        for file_path, functions in analysis_results.items():
            if file_path in comments and sample_count < 3:
                file_comments = comments[file_path]
                for func_info in functions[:2]:  # Show first 2 functions per file
                    func_name = func_info['name']
                    if func_name in file_comments:
                        summary.append(f"\n{func_name}:")
                        summary.append(file_comments[func_name])
                        sample_count += 1
        
        return '\n'.join(summary)
