# script.py

import sys
import json

def main():
    # Example of reading JSON data passed from Node.js
    input_data = json.loads(sys.stdin.read())
    
    # Do some processing (here, just echoing the input)
    result = {
        "message": f"Hello, {input_data['name']}!",
        "data": input_data
    }
    
    # Output the result as JSON
    print(json.dumps(result))

if __name__ == "__main__":
    main()
