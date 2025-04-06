"""
Iniconf - A complete INI configuration management solution for MicroPython.
Provides singleton-based access to configuration values with file handling.
This lib supports comments, and respects the location of items in the file.
Memory usage: 2544 bytes for lib, 5232 bytes with 25 config items
2025-04-06 by klemens@ull.at

Usage:
    # Use default /config.ini
    from iniconf import Iniconf
    config = Iniconf()
    print(config.get('some_key'))  # Automatically loads /config.ini

    # Or use a different file
    config = Iniconf()
    config.set_config_file('other.ini')  # Must be called before first get()
    value = config.get('some_key')  # Loads from other.ini

    # Use in different classes
    class MyClass:
        def __init__(self):
            self.config = Iniconf()  # Gets the same instance
            
        def do_something(self):
            value = self.config.get('some_key')
            # Use the value...

    # Setting values and saving
    config = Iniconf()
    config.set('host', 'localhost')  # Set a value
    config.set('port', 8080)         # Numbers are automatically converted
    config.save()                    # Save to current config file
    config.save('backup.ini')        # Or save to a different file
"""

class Iniconf:
    """
    Complete INI configuration management solution that combines INI file parsing
    with singleton-based access to configuration values.
    
    This class uses the singleton pattern to maintain a single instance of the configuration,
    making it memory efficient for MicroPython applications.
    
    By default, it loads from '/config.ini' on first access. To use a different file,
    call set_config_file() before the first get().
    """
    
    _instance = None  # Stores the single Iniconf instance
    _items = []       # List of (key, value) tuples or comment strings
    config_file = '/config.ini'  # Default config file path
    
    def __new__(cls):
        """
        Override __new__ to implement the singleton pattern.
        This ensures only one Iniconf instance exists.
        
        Returns:
            Iniconf: The single instance of the Iniconf
        """
        if cls._instance is None:
            cls._instance = super(Iniconf, cls).__new__(cls)
            cls._instance._items = []
        return cls._instance
    
    def set_config_file(self, file_path):
        """
        Set the configuration file path before first use.
        Must be called before any get() if not using default /config.ini.
        
        Args:
            file_path (str): Path to the configuration file
            
        Raises:
            RuntimeError: If configuration is already loaded
        """
        if self._items:
            raise RuntimeError("Configuration already loaded, cannot change file path")
        self.config_file = file_path
    
    def loads(self, content):
        """
        Parse INI content string into internal structure.
        
        Args:
            content (str): The INI content to parse
        """
        self._items = []
        
        for line in content.splitlines():
            line = line.strip()
            if not line:
                # Preserve empty lines
                self._items.append(line)
                continue
                
            if line.startswith('#'):
                # Preserve comments
                self._items.append(line)
                continue
                
            if '=' in line:
                # Key-value pair
                key, value = line.split('=', 1)
                self._items.append((key.strip(), value.strip()))
    
    def dumps(self):
        """
        Convert internal structure back to INI string.
        
        Returns:
            str: The INI content as a string
        """
        output = []
        
        for item in self._items:
            if isinstance(item, tuple):
                # Key-value pair
                key, value = item
                output.append(f'{key}={value}')
            else:
                # Empty line or comment
                output.append(item)
                
        return '\n'.join(output)
    
    def get(self, key, default=None):
        """
        Get value for a given key, automatically loading config if needed.
        Converts values to integers when possible.
        
        Args:
            key (str): The key to retrieve
            default: Default value to return if key not found
            
        Returns:
            The value for the key, or default if not found
        """
        if not self._items:
            self.load(self.config_file)
            
        for item in self._items:
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
        """
        Set value for a given key.
        
        Args:
            key (str): The key to set
            value: The value to set
        """
        # Try to update existing key
        for i, item in enumerate(self._items):
            if isinstance(item, tuple):
                k, _ = item
                if k == key:
                    self._items[i] = (key, str(value))
                    return
                    
        # Key doesn't exist, append new one
        self._items.append((key, str(value)))
    
    def load(self, file_path):
        """
        Load configuration from a file.
        
        Args:
            file_path (str): Path to the configuration file
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                self.loads(content)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Initialize with empty config if file can't be loaded
            self._items = []
    
    def save(self, file_path=None):
        """
        Save the current configuration to a file.
        
        Args:
            file_path (str): Optional path where to save the configuration.
                           If None, uses the current config_file.
        """
        target_path = file_path if file_path else self.config_file
        try:
            with open(target_path, 'w') as f:
                content = self.dumps()
                f.write(content)
        except Exception as e:
            print(f"Error saving config: {e}")

# Example usage:
# The if __name__ == "__main__": block at the end of this file contains example code
# that only runs when the file is executed directly (python iniconf.py). When imported
# as a module, this code is ignored. This allows the file to serve both as a library
# and as a self-documenting example.
"""
if __name__ == "__main__":
    # Example 1: Using default /config.ini
    config = Iniconf()
    value = config.get('some_key')  # Automatically loads /config.ini
    
    # Example 2: Using a different file
    config = Iniconf()
    config.set_config_file('other.ini')  # Must be called before first get()
    value = config.get('some_key')  # Loads from other.ini
    
    # Example 3: Using in a class
    class ExampleClass:
        def __init__(self):
            self.config = Iniconf()  # Gets the same instance
            
        def show_config(self):
            print("Host:", self.config.get('host'))
            print("Port:", self.config.get('port'))
    
    # Create instances
    example1 = ExampleClass()
    example2 = ExampleClass()
    
    # Both instances share the same configuration
    example1.show_config()
    example2.show_config() 
"""