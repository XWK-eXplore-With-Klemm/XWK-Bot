# A class for parsing INI files.
# Example usage:

# ini_content = """
# # Database settings
# host=localhost
# port=3306

# # API settings
# url=http://api.example.com
# key=abc123"""

# from ini_parser import IniParser
# parser = IniParser()
# parser.loads(ini_content)

# print(parser.get('host'))  # 'localhost'
# parser.set('port', '5432')
# print(parser.dumps())

class IniParser:

    def __init__(self):
        self.items = []  # List of (key, value) tuples or comment strings
        
    def loads(self, content):
        """Parse INI content string into internal structure"""
        self.items = []
        
        for line in content.splitlines():
            line = line.strip()
            if not line:
                # Preserve empty lines
                self.items.append(line)
                continue
                
            if line.startswith('#'):
                # Preserve comments
                self.items.append(line)
                continue
                
            if '=' in line:
                # Key-value pair
                key, value = line.split('=', 1)
                self.items.append((key.strip(), value.strip()))
    
    def dumps(self):
        """Convert internal structure back to INI string"""
        output = []
        
        for item in self.items:
            if isinstance(item, tuple):
                # Key-value pair
                key, value = item
                output.append(f'{key}={value}')
            else:
                # Empty line or comment
                output.append(item)
                
        return '\n'.join(output)
    
    def get(self, key, default=None):
        """Get value for a given key, convert to int if possible"""
        for item in self.items:
            if isinstance(item, tuple):
                k, v = item
                if k == key:
                    # Try to convert to integer if possible
                    try:
                        return int(v)
                    except ValueError:
                        return v
        return default
    
    def set(self, key, value):
        """Set value for a given key"""
        # Try to update existing key
        for i, item in enumerate(self.items):
            if isinstance(item, tuple):
                k, _ = item
                if k == key:
                    self.items[i] = (key, str(value))
                    return
                    
        # Key doesn't exist, append new one
        self.items.append((key, str(value)))