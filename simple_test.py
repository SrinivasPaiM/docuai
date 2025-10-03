#!/usr/bin/env python3
"""
Simple test script for DocuAI that bypasses problematic dependencies.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def test_simple_analyzer():
    """Test the simple analyzer."""
    print("🔍 Testing Simple Analyzer...")
    
    try:
        from docuai.core.simple_analyzer import SimpleAnalyzer
        
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
        
        test_file = Path("simple_test_sample.py")
        test_file.write_text(test_content)
        
        # Test analyzer
        analyzer = SimpleAnalyzer()
        results = analyzer.analyze_file("simple_test_sample.py")
        
        print(f"✅ Found {len(results)} undocumented functions/classes:")
        for result in results:
            print(f"  - {result['name']} ({result['type']}) at line {result['line']}")
        
        # Clean up
        test_file.unlink()
        return results
        
    except Exception as e:
        print(f"❌ Simple analyzer test failed: {e}")
        return []

def test_simple_generator():
    """Test the simple generator."""
    print("\n🤖 Testing Simple Generator...")
    
    try:
        from docuai.core.simple_generator import SimpleGenerator
        
        generator = SimpleGenerator()
        
        # Test function info
        test_function = {
            'name': 'calculate_sum',
            'type': 'function',
            'line': 1,
            'position': 0
        }
        
        # Generate comment
        comment = generator.generate_comment(test_function, 'python')
        print("✅ Generated comment:")
        print(comment)
        
        return True
        
    except Exception as e:
        print(f"❌ Simple generator test failed: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow."""
    print("\n🔄 Testing Complete Workflow...")
    
    try:
        from docuai.core.simple_analyzer import SimpleAnalyzer
        from docuai.core.simple_generator import SimpleGenerator
        
        # Create test file
        test_content = '''def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    def __init__(self):
        self.cache = {}
    
    def factorial(self, n):
        if n <= 1:
            return 1
        return n * self.factorial(n-1)
'''
        
        test_file = Path("workflow_test.py")
        test_file.write_text(test_content)
        
        # Analyze
        analyzer = SimpleAnalyzer()
        results = analyzer.analyze_file("workflow_test.py")
        
        print(f"Found {len(results)} undocumented items:")
        
        # Generate comments
        generator = SimpleGenerator()
        for result in results:
            comment = generator.generate_comment(result, 'python')
            print(f"\n{result['name']} ({result['type']}):")
            print(comment)
        
        # Clean up
        test_file.unlink()
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

def main():
    """Run simple tests."""
    print("🚀 DocuAI Simple Test (No AI Dependencies)")
    print("=" * 60)
    
    # Test analyzer
    results = test_simple_analyzer()
    
    # Test generator
    generator_ok = test_simple_generator()
    
    # Test complete workflow
    workflow_ok = test_complete_workflow()
    
    print("\n📊 Test Results:")
    print(f"  Analyzer: {'✅ PASS' if results else '❌ FAIL'}")
    print(f"  Generator: {'✅ PASS' if generator_ok else '❌ FAIL'}")
    print(f"  Workflow: {'✅ PASS' if workflow_ok else '❌ FAIL'}")
    
    if results and generator_ok and workflow_ok:
        print("\n🎉 All tests passed! DocuAI simple mode is working.")
        print("\n💡 To fix the original 'docuai test' command:")
        print("   1. Install missing dependencies: pip install torch transformers")
        print("   2. Or use the fast config: docuai test --config config_fast.yaml")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
