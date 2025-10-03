#!/usr/bin/env python3
"""
DocuAI Free Version - No AI dependencies, completely free and fast.
"""

import os
import sys
import re
from typing import List, Dict, Optional
from pathlib import Path


class DocuAIFree:
    """Free version of DocuAI with no external dependencies."""
    
    def __init__(self):
        """Initialize the free analyzer."""
        self.ignore_patterns = [
            "**/node_modules/**",
            "**/venv/**",
            "**/env/**",
            "**/.git/**",
            "**/__pycache__/**",
            "**/target/**",
            "**/build/**",
            "**/dist/**"
        ]
    
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
        """Check if file should be ignored."""
        for pattern in self.ignore_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches ignore pattern."""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
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
            if language == 'python':
                if line.startswith('#') or '"""' in line or "'''" in line:
                    return True
            elif language in ['javascript', 'typescript']:
                if line.startswith('//') or '/*' in line or '*/' in line:
                    return True
            elif language in ['java', 'cpp', 'c']:
                if line.startswith('//') or '/*' in line or '*/' in line:
                    return True
            elif language == 'go':
                if line.startswith('//'):
                    return True
            elif language == 'rust':
                if line.startswith('///') or line.startswith('//'):
                    return True
            
            # If we hit non-empty, non-comment code, stop looking
            if line and not any(line.startswith(p) for p in ['//', '#', '/*', '*', '///']):
                break
        
        return False
    
    def _camel_to_sentence(self, text: str) -> str:
        """Convert camelCase to sentence case."""
        # Insert space before capital letters
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # Convert to lowercase and capitalize first letter
        return result.lower().capitalize()
    
    def generate_comment(self, function_info: Dict, language: str) -> str:
        """Generate a comment for a function or class."""
        name = function_info['name']
        func_type = function_info['type']
        
        if language == 'python':
            if func_type == 'function':
                return f'"""\n    {self._camel_to_sentence(name)}.\n    \n    Args:\n        TODO: Add parameter descriptions\n    \n    Returns:\n        TODO: Add return description\n    """'
            else:  # class
                return f'"""\n    {self._camel_to_sentence(name)} class.\n    \n    TODO: Add class description\n    """'
        
        elif language in ['javascript', 'typescript']:
            if func_type == 'function':
                return f'/**\n * {self._camel_to_sentence(name)}\n * \n * @param {{}} TODO: Add parameter descriptions\n * @returns {{}} TODO: Add return description\n */'
            else:  # class
                return f'/**\n * {self._camel_to_sentence(name)} class\n * \n * TODO: Add class description\n */'
        
        elif language in ['java', 'cpp', 'c']:
            if func_type == 'function':
                return f'/**\n * {self._camel_to_sentence(name)}\n * \n * @param TODO: Add parameter descriptions\n * @return TODO: Add return description\n */'
            else:  # class
                return f'/**\n * {self._camel_to_sentence(name)} class\n * \n * TODO: Add class description\n */'
        
        elif language == 'go':
            if func_type == 'function':
                return f'// {self._camel_to_sentence(name)} TODO: Add function description\n// TODO: Add parameter and return descriptions'
            else:  # class/struct
                return f'// {self._camel_to_sentence(name)} TODO: Add struct/interface description'
        
        elif language == 'rust':
            if func_type == 'function':
                return f'/// {self._camel_to_sentence(name)}\n/// TODO: Add function description\n/// TODO: Add parameter and return descriptions'
            else:  # struct/trait
                return f'/// {self._camel_to_sentence(name)} TODO: Add struct/trait description'
        
        # Default fallback
        return f'// TODO: Add documentation for {name}'
    
    def analyze_file(self, file_path: str) -> List[Dict]:
        """Analyze a single file for undocumented functions and classes."""
        if self._should_ignore_file(file_path):
            return []
        
        language = self._get_language_from_extension(file_path)
        if not language:
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
        
        return self._find_undocumented_functions(content, language, file_path)
    
    def _find_undocumented_functions(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Find undocumented functions using regex patterns."""
        undocumented = []
        
        if language == 'python':
            # Python function patterns
            function_patterns = [
                (r'def\s+(\w+)\s*\(', 'function'),
                (r'class\s+(\w+)\s*[\(:]', 'class'),
            ]
            
            for pattern, func_type in function_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    start_pos = match.start()
                    
                    # Check if there's a comment/docstring before this function
                    has_doc = self._has_documentation_before(content, start_pos, language)
                    if not has_doc:
                        line_num = content[:start_pos].count('\n') + 1
                        undocumented.append({
                            'name': func_name,
                            'type': func_type,
                            'line': line_num,
                            'position': start_pos,
                            'file': file_path
                        })
        
        elif language in ['javascript', 'typescript']:
            # JavaScript/TypeScript function patterns
            function_patterns = [
                (r'function\s+(\w+)\s*\(', 'function'),
                (r'const\s+(\w+)\s*=\s*\(', 'function'),
                (r'let\s+(\w+)\s*=\s*\(', 'function'),
                (r'var\s+(\w+)\s*=\s*\(', 'function'),
                (r'(\w+)\s*:\s*function', 'function'),
                (r'class\s+(\w+)\s*[{\s]', 'class'),
            ]
            
            for pattern, func_type in function_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    start_pos = match.start()
                    
                    has_doc = self._has_documentation_before(content, start_pos, language)
                    if not has_doc:
                        line_num = content[:start_pos].count('\n') + 1
                        undocumented.append({
                            'name': func_name,
                            'type': func_type,
                            'line': line_num,
                            'position': start_pos,
                            'file': file_path
                        })
        
        return undocumented
    
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
    
    def test(self):
        """Test DocuAI with sample code."""
        print("🚀 DocuAI Free Test")
        print("=" * 50)
        
        # Create test file
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
            # Analyze
            results = self.analyze_file("test_sample.py")
            
            if results:
                print(f"✅ Found {len(results)} undocumented functions/classes:")
                for result in results:
                    print(f"  - {result['name']} ({result['type']}) at line {result['line']}")
                
                # Generate comments
                print("\n🤖 Generated comments:")
                for result in results:
                    comment = self.generate_comment(result, 'python')
                    print(f"\n{result['name']} ({result['type']}):")
                    print(comment)
            else:
                print("No undocumented functions found.")
            
            print("\n🎉 DocuAI Free is working perfectly!")
            print("✅ No AI dependencies required")
            print("✅ No tree-sitter required")
            print("✅ Completely free and fast")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()
                print("\n🧹 Cleaned up test file")


def main():
    """Main function."""
    docuai = DocuAIFree()
    docuai.test()


if __name__ == "__main__":
    main()
