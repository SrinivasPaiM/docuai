"""
Simple comment generator that doesn't require AI models.
"""

import re
from typing import Dict


class SimpleGenerator:
    """Simple comment generator using rule-based approach."""
    
    def __init__(self):
        """Initialize the simple generator."""
        pass
    
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
