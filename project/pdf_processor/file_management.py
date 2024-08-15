# src/pdf_processor/file_management.py

import os

def get_xlsx_files(directory):
    """Returns a list of all .xlsx files in the given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.xlsx')]
