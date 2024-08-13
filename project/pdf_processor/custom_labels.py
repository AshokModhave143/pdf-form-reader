import json
import os
import sys

def load_custom_labels(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    custom_labels_path = os.path.join("mappings", f"{base_name}.json")
    
    if os.path.exists(custom_labels_path):
        with open(custom_labels_path, 'r') as f:
            custom_labels = json.load(f)
        return custom_labels
    else:
        print(f"Custom labels file {custom_labels_path} not found.")
        sys.exit(1)
