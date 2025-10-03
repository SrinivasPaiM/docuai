"""
Sample Python code with undocumented functions and classes for testing DocuAI.
"""

def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_user_data(users):
    result = []
    for user in users:
        if user.get('active', False):
            processed_user = {
                'id': user['id'],
                'name': user['name'].upper(),
                'email': user['email'].lower()
            }
            result.append(processed_user)
    return result

def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}
    
    def process(self, data):
        if data in self.cache:
            return self.cache[data]
        
        result = self._transform_data(data)
        self.cache[data] = result
        return result
    
    def _transform_data(self, data):
        return [item * 2 for item in data if isinstance(item, (int, float))]

class UserManager:
    def __init__(self, database):
        self.db = database
        self.users = []
    
    def add_user(self, user_data):
        if self.validate_user(user_data):
            self.users.append(user_data)
            return True
        return False
    
    def get_user(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
    
    def validate_user(self, user):
        return 'name' in user and 'email' in user
