from collections import OrderedDict
import ujson  # Still needed for parsing

# formats json dump
class xwkJson:
    @staticmethod
    def format_json(obj, indent=4):
        """Format JSON without recursion"""
        if not obj:
            return "{}"
            
        # Simple non-recursive implementation
        result = []
        stack = [(obj, 0)]  # (value, depth) pairs
        
        while stack:
            value, depth = stack.pop()
            indent_str = " " * (depth * indent)
            
            if isinstance(value, dict):
                if not value:
                    result.append(indent_str + "{}")
                    continue
                    
                result.append(indent_str + "{")
                items = list(value.items())
                # Add items in reverse order since we're using a stack
                for i, (k, v) in reversed(list(enumerate(items))):
                    stack.append((("," if i < len(items)-1 else ""), depth))
                    stack.append((v, depth + 1))
                    result.append(indent_str + f'    "{k}": ')
                result.append(indent_str + "}")
                
            elif isinstance(value, (list, tuple)):
                if not value:
                    result.append(indent_str + "[]")
                    continue
                    
                result.append(indent_str + "[")
                # Add items in reverse order
                for i, item in reversed(list(enumerate(value))):
                    stack.append((("," if i < len(value)-1 else ""), depth))
                    stack.append((item, depth + 1))
                result.append(indent_str + "]")
                
            elif isinstance(value, str):
                result.append(indent_str + f'"{value}"')
            elif isinstance(value, bool):
                result.append(indent_str + str(value).lower())
            elif value is None:
                result.append(indent_str + "null")
            else:
                result.append(indent_str + str(value))
                
        return "".join(result)

    @staticmethod
    def _convert_to_ordered(obj):
        if isinstance(obj, dict):
            return OrderedDict((k, xwkJson._convert_to_ordered(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return [xwkJson._convert_to_ordered(item) for item in obj]
        return obj

    @staticmethod
    def dumps(obj):
        """Convert object to formatted JSON string"""
        return xwkJson.format_json(obj)

    @staticmethod
    def dump(obj, fp):
        """Write object as formatted JSON to file"""
        formatted = xwkJson.dumps(obj)
        fp.write(formatted)

    @staticmethod
    def loads(s):
        """Load JSON string and return OrderedDict"""
        try:
            obj = ujson.loads(s)  # Still use ujson for parsing
            return xwkJson._convert_to_ordered(obj)
        except Exception as e:
            print("Error parsing JSON:", e)
            raise

    @staticmethod
    def load(fp):
        """Load JSON file and return OrderedDict"""
        try:
            content = fp.read()
            return xwkJson.loads(content)
        except Exception as e:
            print("Error loading JSON file:", e)
            raise