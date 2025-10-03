"""
AI-powered comment generation module using free models.
"""

import os
import re
from typing import List, Dict, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline,
    set_seed
)
import yaml


class AICommentGenerator:
    """Generates code comments using free AI models."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the AI generator with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.ai_config = self.config['ai']
        self.model_name = self.ai_config['model_name']
        self.max_tokens = self.ai_config['max_tokens']
        self.temperature = self.ai_config['temperature']
        self.use_local_model = self.ai_config['use_local_model']
        
        # Initialize model and tokenizer
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._setup_model()
    
    def _setup_model(self):
        """Setup the AI model for comment generation."""
        try:
            if self.use_local_model and self.model_name != "rule-based":
                print("Loading local model...")
                # Use a smaller, free model that's good for code generation
                model_name = self.model_name
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                # Add padding token if it doesn't exist
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Create text generation pipeline
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_length=self.max_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
            else:
                # Use rule-based generation (no AI model)
                print("Using rule-based comment generation...")
                self.model = None
                self.pipeline = None
                
        except Exception as e:
            print(f"Error setting up model: {e}")
            print("Falling back to rule-based comment generation...")
            self.model = None
            self.pipeline = None
    
    def _generate_rule_based_comment(self, function_info: Dict, language: str) -> str:
        """Generate comments using rule-based approach as fallback."""
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
    
    def _camel_to_sentence(self, text: str) -> str:
        """Convert camelCase to sentence case."""
        # Insert space before capital letters
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # Convert to lowercase and capitalize first letter
        return result.lower().capitalize()
    
    def _generate_ai_comment(self, function_info: Dict, language: str, context: str = "") -> str:
        """Generate comment using AI model."""
        if not self.pipeline:
            return self._generate_rule_based_comment(function_info, language)
        
        try:
            name = function_info['name']
            func_type = function_info['type']
            
            # Create prompt for the AI model
            prompt = self._create_prompt(name, func_type, language, context)
            
            # Generate comment
            result = self.pipeline(
                prompt,
                max_length=len(prompt.split()) + self.max_tokens,
                num_return_sequences=1,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = result[0]['generated_text']
            comment = self._extract_comment_from_generated(generated_text, prompt, language)
            
            return comment if comment else self._generate_rule_based_comment(function_info, language)
            
        except Exception as e:
            print(f"Error generating AI comment: {e}")
            return self._generate_rule_based_comment(function_info, language)
    
    def _create_prompt(self, name: str, func_type: str, language: str, context: str) -> str:
        """Create a prompt for the AI model."""
        base_prompt = f"Generate a {language} {func_type} comment for '{name}'"
        
        if context:
            base_prompt += f" with context: {context[:200]}..."
        
        if language == 'python':
            base_prompt += ". Use docstring format with triple quotes."
        elif language in ['javascript', 'typescript']:
            base_prompt += ". Use JSDoc format with /** */."
        elif language in ['java', 'cpp', 'c']:
            base_prompt += ". Use JavaDoc format with /** */."
        elif language == 'go':
            base_prompt += ". Use Go comment format with //."
        elif language == 'rust':
            base_prompt += ". Use Rust documentation format with ///."
        
        return base_prompt
    
    def _extract_comment_from_generated(self, generated_text: str, prompt: str, language: str) -> str:
        """Extract the comment from generated text."""
        # Remove the prompt from generated text
        comment = generated_text.replace(prompt, "").strip()
        
        # Clean up the comment based on language
        if language == 'python':
            # Ensure it starts with """
            if not comment.startswith('"""'):
                comment = '"""\n    ' + comment
            if not comment.endswith('"""'):
                comment += '\n    """'
        
        elif language in ['javascript', 'typescript', 'java', 'cpp', 'c']:
            # Ensure it starts with /**
            if not comment.startswith('/**'):
                comment = '/**\n * ' + comment
            if not comment.endswith('*/'):
                comment += '\n */'
        
        elif language == 'go':
            # Ensure it starts with //
            if not comment.startswith('//'):
                comment = '// ' + comment
        
        elif language == 'rust':
            # Ensure it starts with ///
            if not comment.startswith('///'):
                comment = '/// ' + comment
        
        return comment
    
    def generate_comment(self, function_info: Dict, language: str, context: str = "") -> str:
        """Generate a comment for a function or class."""
        return self._generate_ai_comment(function_info, language, context)
    
    def generate_comments_batch(self, functions: List[Dict], language: str) -> Dict[str, str]:
        """Generate comments for multiple functions."""
        comments = {}
        
        for func_info in functions:
            name = func_info['name']
            comment = self.generate_comment(func_info, language)
            comments[name] = comment
        
        return comments
