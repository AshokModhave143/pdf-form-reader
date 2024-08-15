from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import json

from project.pdf_processor.custom_labels import load_custom_labels
from project.pdf_processor.excel_generation import generate_excel
from project.pdf_processor.form_extraction import extract_form_fields
from project.pdf_processor.json_template import prepare_json_template_data
from project.pdf_processor.file_management import get_xlsx_files

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXCEL_FOLDER = 'downloads'
MAPPINGS_FOLDER = 'mappings'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXCEL_FOLDER'] = EXCEL_FOLDER
app.config['MAPPINGS_FOLDER'] = MAPPINGS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(MAPPINGS_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['pdf_file']
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            if 'prepare_json' in request.form:
                json_data = prepare_json_template_data(file_path)
                return render_template('_json_preview.html', json_data=json.dumps(json_data, indent=4), pdf_file=file.filename)

            elif 'process_pdf' in request.form:
                custom_labels = load_custom_labels(file_path)
                form_data = extract_form_fields(file_path, custom_labels)

                return render_template('_table_preview.html', form_data=form_data, json_data=json.dumps({'form_fields': form_data}, indent=4), pdf_file=file.filename)
    
    return render_template('_upload.html')

@app.route('/review_mappings', methods=['GET'])
def review_mappings():
    mappings_files = os.listdir(app.config['MAPPINGS_FOLDER'])
    return render_template('_review_mappings.html', mappings_files=mappings_files)

@app.route('/edit_mapping/<filename>', methods=['GET', 'POST'])
def edit_mapping(filename):
    file_path = os.path.join(app.config['MAPPINGS_FOLDER'], filename)

    if request.method == 'POST':
        json_data = request.form['json_data']
        with open(file_path, 'w') as json_file:
            json_file.write(json_data)
        return redirect(url_for('review_mappings'))

    with open(file_path, 'r') as json_file:
        json_data = json_file.read()
    return render_template('_json_preview.html', json_data=json_data, pdf_file=filename)

@app.route('/save_json/<pdf_file>', methods=['POST'])
def save_json(pdf_file):
    json_data = request.form['json_data']
    base_name = os.path.splitext(pdf_file)[0]
    json_template_path = os.path.join(app.config['MAPPINGS_FOLDER'], f"{base_name}.json")

    with open(json_template_path, 'w') as json_file:
        json_file.write(json_data)

    return redirect(url_for('index'))

@app.route('/export_excel', methods=['POST'])
def export_excel():
    json_data = request.form['json_data']
    form_data = json.loads(json_data)['form_fields']
    excel_path = os.path.join(app.config['EXCEL_FOLDER'], 'form_data.xlsx')
    
    generate_excel(form_data, excel_path)
    
    return render_template('_table_preview.html', form_data=form_data, excel_file='form_data.xlsx')

@app.route('/review_downloads', methods=['GET'])
def review_downloads():
    # Use the get_xlsx_files function to get a list of xlsx files
    xlsx_files = get_xlsx_files(app.config['EXCEL_FOLDER'])
    return render_template('_downloads.html', xlsx_files=xlsx_files)

@app.route('/download/excel/<filename>', methods=['GET'])
def download_excel(filename):
    try:
        file_path = os.path.join(app.config['EXCEL_FOLDER'], filename)
        if os.path.isfile(file_path):
            return send_from_directory(
                app.config['UPLOAD_FOLDER'], filename, as_attachment=True
            )
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
