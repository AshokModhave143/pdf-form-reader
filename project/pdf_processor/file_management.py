import os
import json
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

def handle_export_excel(request, excel_folder):
    json_data = request.form['json_data']
    form_data = json.loads(json_data)['form_fields']
    pdf_filename = request.form.get('pdf_file')
    base_name = os.path.splitext(pdf_filename)[0]
    excel_filename = f"{base_name}.xlsx"

    excel_path = os.path.join(excel_folder, excel_filename)

    generate_excel(form_data, excel_path)
    
    return render_template('_table_preview.html', form_data=form_data, excel_file=excel_filename)

def get_xlsx_files(excel_folder):
    return os.listdir(excel_folder)

def download_excel(filename, excel_folder):
    file_path = os.path.join(excel_folder, filename)
    if os.path.isfile(file_path):
        return send_from_directory(excel_folder, filename, as_attachment=True)
    return "File not found", 404
