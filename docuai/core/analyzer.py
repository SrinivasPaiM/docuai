"""
Code analyzer module for detecting undocumented functions and classes.
"""

import os
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import tree_sitter
from tree_sitter import Language, Parser
import yaml


class CodeAnalyzer:
    """Analyzes code to find undocumented functions and classes."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the analyzer with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.supported_languages = self.config['code_analysis']['supported_languages']
        self.comment_patterns = self.config['code_analysis']['comment_patterns']
        self.ignore_patterns = self.config['code_analysis']['ignore_patterns']
        
        # Initialize tree-sitter parsers
        self.parsers = {}
        self._setup_parsers()
    
    def _setup_parsers(self):
        """Setup tree-sitter parsers for supported languages."""
        try:
            # Try to load language libraries - fixed constructor calls
            languages = {
                'python': tree_sitter.Language('tree_sitter_python'),
                'javascript': tree_sitter.Language('tree_sitter_javascript'),
                'typescript': tree_sitter.Language('tree_sitter_typescript'),
                'java': tree_sitter.Language('tree_sitter_java'),
                'cpp': tree_sitter.Language('tree_sitter_cpp'),
                'c': tree_sitter.Language('tree_sitter_c'),
                'go': tree_sitter.Language('tree_sitter_go'),
                'rust': tree_sitter.Language('tree_sitter_rust'),
            }
            
            for lang_name, lang in languages.items():
                parser = Parser()
                parser.set_language(lang)
                self.parsers[lang_name] = parser
                
        except Exception as e:
            print(f"Warning: Could not load all tree-sitter parsers: {e}")
            # Fallback to regex-based analysis
            self.parsers = {}
    
    def _get_language_from_extension(self, file_path: str) -> Optional[str]:
        """Determine language from file extension."""
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
        return ext_to_lang.get(ext)
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns."""
        for pattern in self.ignore_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches ignore pattern."""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def _extract_comments_regex(self, content: str, language: str) -> List[Tuple[int, int, str]]:
        """Extract comments using regex patterns."""
        comments = []
        patterns = self.comment_patterns.get(language, [])
        
        for pattern in patterns:
            if pattern == "//":
                # Single line comments
                for match in re.finditer(r'//.*$', content, re.MULTILINE):
                    comments.append((match.start(), match.end(), match.group()))
            elif pattern == "/*":
                # Multi-line comments
                for match in re.finditer(r'/\*.*?\*/', content, re.DOTALL):
                    comments.append((match.start(), match.end(), match.group()))
            elif pattern == "#":
                # Python-style comments
                for match in re.finditer(r'#.*$', content, re.MULTILINE):
                    comments.append((match.start(), match.end(), match.group()))
            elif pattern == '"""':
                # Python docstrings
                for match in re.finditer(r'""".*?"""', content, re.DOTALL):
                    comments.append((match.start(), match.end(), match.group()))
            elif pattern == "'''":
                # Python docstrings
                for match in re.finditer(r"'''.*?'''", content, re.DOTALL):
                    comments.append((match.start(), match.end(), match.group()))
        
        return comments
    
    def _find_undocumented_functions_regex(self, content: str, language: str) -> List[Dict]:
        """Find undocumented functions using regex patterns."""
        undocumented = []
        
        if language == 'python':
            # Python function patterns
            function_patterns = [
                r'def\s+(\w+)\s*\(',
                r'class\s+(\w+)\s*[\(:]',
            ]
            
            for pattern in function_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    start_pos = match.start()
                    
                    # Check if there's a comment/docstring before this function
                    has_doc = self._has_documentation_before(content, start_pos, language)
                    if not has_doc:
                        undocumented.append({
                            'name': func_name,
                            'type': 'function' if 'def' in pattern else 'class',
                            'line': content[:start_pos].count('\n') + 1,
                            'position': start_pos
                        })
        
        elif language in ['javascript', 'typescript']:
            # JavaScript/TypeScript function patterns
            function_patterns = [
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*\(',
                r'let\s+(\w+)\s*=\s*\(',
                r'var\s+(\w+)\s*=\s*\(',
                r'(\w+)\s*:\s*function',
                r'class\s+(\w+)\s*[{\s]',
            ]
            
            for pattern in function_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    start_pos = match.start()
                    
                    has_doc = self._has_documentation_before(content, start_pos, language)
                    if not has_doc:
                        undocumented.append({
                            'name': func_name,
                            'type': 'function' if 'function' in pattern or '=' in pattern else 'class',
                            'line': content[:start_pos].count('\n') + 1,
                            'position': start_pos
                        })
        
        return undocumented
    
    def _has_documentation_before(self, content: str, position: int, language: str) -> bool:
        """Check if there's documentation before the given position."""
        before_content = content[:position]
        lines = before_content.split('\n')
        
        # Look at the last few lines before the position
        for line in reversed(lines[-5:]):
            line = line.strip()
            if not line:
                continue
            
            # Check for comment patterns
            comment_patterns = self.comment_patterns.get(language, [])
            for pattern in comment_patterns:
                if pattern == "//" and line.startswith('//'):
                    return True
                elif pattern == "/*" and ('/*' in line or '*/' in line):
                    return True
                elif pattern == "#" and line.startswith('#'):
                    return True
                elif pattern in ['"""', "'''"] and (pattern in line):
                    return True
            
            # If we hit non-empty, non-comment code, stop looking
            if line and not any(line.startswith(p) for p in ['//', '#', '/*', '*']):
                break
        
        return False
    
    def analyze_file(self, file_path: str) -> List[Dict]:
        """Analyze a single file for undocumented functions/classes."""
        if self._should_ignore_file(file_path):
            return []
        
        language = self._get_language_from_extension(file_path)
        if not language or language not in self.supported_languages:
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
        
        # Use tree-sitter if available, otherwise fallback to regex
        if language in self.parsers:
            return self._analyze_with_tree_sitter(content, language, file_path)
        else:
            return self._find_undocumented_functions_regex(content, language)
    
    def _analyze_with_tree_sitter(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Analyze code using tree-sitter parser."""
        parser = self.parsers[language]
        tree = parser.parse(bytes(content, 'utf8'))
        
        undocumented = []
        
        def traverse_node(node, depth=0):
            if node.type in ['function_definition', 'class_definition', 'method_definition']:
                # Check if this function/class has documentation
                has_doc = self._check_node_documentation(node, content)
                if not has_doc:
                    name = self._extract_node_name(node, content)
                    if name:
                        undocumented.append({
                            'name': name,
                            'type': 'function' if 'function' in node.type else 'class',
                            'line': node.start_point[0] + 1,
                            'position': node.start_byte,
                            'file': file_path
                        })
            
            for child in node.children:
                traverse_node(child, depth + 1)
        
        traverse_node(tree.root_node)
        return undocumented
    
    def _check_node_documentation(self, node, content: str) -> bool:
        """Check if a node has documentation."""
        # Look for docstrings or comments before the node
        start_byte = node.start_byte
        before_content = content[:start_byte]
        
        # Check last few lines for comments/docstrings
        lines = before_content.split('\n')
        for line in reversed(lines[-3:]):
            line = line.strip()
            if line.startswith('#') or line.startswith('//') or '"""' in line or "'''" in line:
                return True
            if line and not line.startswith(('//', '#', '/*', '*')):
                break
        
        return False
    
    def _extract_node_name(self, node, content: str) -> Optional[str]:
        """Extract the name from a tree-sitter node."""
        for child in node.children:
            if child.type == 'identifier':
                start_byte = child.start_byte
                end_byte = child.end_byte
                return content[start_byte:end_byte]
        return None
    
    def analyze_directory(self, directory: str) -> Dict[str, List[Dict]]:
        """Analyze all files in a directory."""
        results = {}
        
        for root, dirs, files in os.walk(directory):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_file(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not self._should_ignore_file(file_path):
                    undocumented = self.analyze_file(file_path)
                    if undocumented:
                        results[file_path] = undocumented
        
        return results
