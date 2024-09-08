import os
import json
import re
import pandas as pd
from flask import render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from project.pdf_processor.custom_labels import load_custom_labels
from project.pdf_processor.excel_generation import generate_excel
from project.pdf_processor.form_extraction import extract_form_fields
from project.pdf_processor.json_template import prepare_json_template_data

def handle_index_post_request(request, upload_folder):
    file = request.files['pdf_file']
    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(upload_folder, secure_filename(file.filename))
        file.save(file_path)

        if 'prepare_json' in request.form:
            json_data = prepare_json_template_data(file_path)
            return render_template('_json_preview.html', json_data=json.dumps(json_data, indent=4), pdf_file=file.filename)

        elif 'process_pdf' in request.form:
            custom_labels = load_custom_labels(file_path)
            form_data = extract_form_fields(file_path, custom_labels)
            return render_template('_table_preview.html', form_data=form_data, json_data=json.dumps({'form_fields': form_data}, indent=4), pdf_file=file.filename)
    return render_template('_upload.html')

def get_mappings_files(mappings_folder):
    return os.listdir(mappings_folder)

def handle_edit_mapping(request, filename, mappings_folder):
    file_path = os.path.join(mappings_folder, filename)
    if request.method == 'POST':
        json_data = request.form['json_data']
        with open(file_path, 'w') as json_file:
            json_file.write(json_data)
        return redirect(url_for('review_mappings'))

    with open(file_path, 'r') as json_file:
        json_data = json_file.read()
    return render_template('_json_preview.html', json_data=json_data, pdf_file=filename)

def save_json_template(request, pdf_file, mappings_folder):
    json_data = request.form['json_data']
    base_name = os.path.splitext(pdf_file)[0]
    json_template_path = os.path.join(mappings_folder, f"{base_name}.json")

    with open(json_template_path, 'w') as json_file:
        json_file.write(json_data)

def handle_export_excel(request, filename, excel_folder):
    json_data = request.form['json_data']
    form_data = json.loads(json_data)['form_fields']
    base_name = os.path.splitext(filename)[0]
    excel_filename = f"{base_name}.xlsx"

    excel_path = os.path.join(excel_folder, excel_filename)
    generate_excel(form_data, excel_path)
    return render_template('_table_preview.html', form_data=form_data, pdf_file=filename, excel_file=excel_filename)

def get_xlsx_files(excel_folder):
    return os.listdir(excel_folder)

def download_excel(filename, excel_folder):
    abs_folder = os.path.abspath(excel_folder)
    file_path = os.path.join(abs_folder, filename)
    if os.path.isfile(file_path):
        return send_from_directory(abs_folder, filename, as_attachment=True)
    return "File not found", 404

def handle_compare_files(request, uploadFolder):
    # pdf file processing
    pdf_file = request.files['pdf_file']
    pdf_file_path, pdf_file_name = process_file(pdf_file, uploadFolder)


    # excel file processing
    excel_file = request.files['excel_file']
    excel_file_path, excel_file_name = process_file(excel_file, uploadFolder)

    if pdf_file_path and excel_file_path:
        pdf_form_data, excel_json_data, comparison_results = compare_pdfs(pdf_file_path, excel_file_path)
        return render_template('_compare_files.html', pdf_form_data=pdf_form_data, pdf_file_name=pdf_file_name, excel_json_data=excel_json_data, excel_file_name=excel_file_name, comparison_results=comparison_results)
    return "File not found", 404

def process_file(file, upload_folder):
    """Save the uploaded PDF file and return the saved path."""
    if file and (file.filename.endswith('.pdf') or (file.filename.endswith('.xls') or file.filename.endswith('.xlsx'))):
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_name=file.filename
        return file_path, file_name
    return None

def compare_pdfs(pdf_file_path, excel_file_path):
    """Compare data from a PDF form file and an Excel file and return comparison data.""" 
    
    # Extract form data from the PDF file
    pdf_form_data, pdf_json_data = handle_process_pdf(pdf_file_path)
    
    # Read and extract data from the Excel file
    excel_json_data = read_excel_file(excel_file_path)
    
    comparison_results = []
    
     # Convert pdf_form_data to a list of tuples
    pdf_items = list(pdf_form_data.items())
    
    # Use zip to iterate over both pdf_items and excel_json_data
    for (key, pdf_item), excel_item in zip(pdf_items, excel_json_data):
        # Compare the PDF and Excel values
        is_same = compare_items(pdf_item, excel_item)

        # Append the comparison result
        comparison_results.append({
            'field_name': key,
            'pdf_value': pdf_item,
            'excel_value': excel_item,
            'is_same': is_same
        })
    
    # Return the data and comparison results
    return pdf_form_data, excel_json_data, comparison_results

def compare_items(pdf_item, excel_item):
    is_same_label=pdf_item.get('label') == excel_item.get('label')
    is_same_customLabel=pdf_item.get('customLabel') == excel_item.get('customLabel')
    is_same_value=pdf_item.get('value') == excel_item.get('value')
    return is_same_label and is_same_customLabel and is_same_value

def handle_process_pdf(file_path):
   if file_path:
        custom_labels = load_custom_labels(file_path)
        form_data = extract_form_fields(file_path, custom_labels)
        json_data=json.dumps({'form_fields': form_data}, indent=4) 
        return form_data, json_data
   

def to_camel_case(s):
    words = re.split(r'[\s_]+', s.strip())
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def replace_nan_with_empty_string(data):
    # Recursively replace NaN with an empty string in nested dictionaries/lists
    if isinstance(data, list):
        return [replace_nan_with_empty_string(item) for item in data]
    elif isinstance(data, dict):
        return {key: replace_nan_with_empty_string(value) for key, value in data.items()}
    elif pd.isna(data):
        return ""
    else:
        return data

def read_excel_file(file_path):
    try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)

        # Convert the headers to kebab-case
        df.columns = [to_camel_case(col) for col in df.columns]

         # Convert the DataFrame to a list of dictionaries (JSON format)
        data_list = df.to_dict(orient='records')
        
        # Convert the list of dictionaries to JSON format
        json_data = replace_nan_with_empty_string(data_list)
        
        return json_data
    
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}
