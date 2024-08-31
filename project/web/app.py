from flask import Flask, request, render_template, redirect, url_for
import os
from project.pdf_processor.file_management import (
    handle_index_post_request, get_mappings_files, handle_edit_mapping, 
    save_json_template, handle_export_excel, get_xlsx_files, download_excel, handle_compare_files
)

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
        return handle_index_post_request(request, app.config['UPLOAD_FOLDER'])
    return render_template('_upload.html')

@app.route('/review_mappings', methods=['GET'])
def review_mappings():
    mappings_files = get_mappings_files(app.config['MAPPINGS_FOLDER'])
    return render_template('_review_mappings.html', mappings_files=mappings_files)

@app.route('/edit_mapping/<filename>', methods=['GET', 'POST'])
def edit_mapping(filename):
    return handle_edit_mapping(request, filename, app.config['MAPPINGS_FOLDER'])

@app.route('/save_json/<pdf_file>', methods=['POST'])
def save_json(pdf_file):
    save_json_template(request, pdf_file, app.config['MAPPINGS_FOLDER'])
    return redirect(url_for('index'))

@app.route('/export_excel', methods=['POST'])
def export_excel():
    return handle_export_excel(request, app.config['EXCEL_FOLDER'])

@app.route('/review_downloads', methods=['GET'])
def review_downloads():
    xlsx_files = get_xlsx_files(app.config['EXCEL_FOLDER'])
    return render_template('_downloads.html', xlsx_files=xlsx_files)

@app.route('/download/excel/<filename>', methods=['GET'])
def process_download_excel(filename):
    excel_folder = app.config['EXCEL_FOLDER']
    # Call the function to download the specified Excel file
    return download_excel(filename, excel_folder)

@app.route('/compare_files', methods=['GET', 'POST'])
def compare_files():
    if request.method == 'POST':
        return handle_compare_files(request, app.config['UPLOAD_FOLDER'])
    return render_template('_compare_files.html')


if __name__ == '__main__':
    app.run(debug=True)
