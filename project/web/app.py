from flask import Flask, request, render_template, send_from_directory
import os
import json

from pdf_processor import load_custom_labels, prepare_json_template, generate_excel, extract_form_fields

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXCEL_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXCEL_FOLDER'] = EXCEL_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'prepare_json' in request.form:
            file = request.files['pdf_file']
            if file and file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                prepare_json_template(file_path)
                return "JSON template prepared successfully."
        elif 'process_pdf' in request.form:
            file = request.files['pdf_file']
            if file and file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                
                custom_labels = load_custom_labels(file_path)
                form_data = extract_form_fields(file_path, custom_labels)

                json_output = json.dumps({'form_fields': form_data}, indent=4)
                
                # Save JSON output
                json_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'form_data.json')
                with open(json_output_path, 'w') as json_file:
                    json_file.write(json_output)
                
                excel_path = os.path.join(app.config['EXCEL_FOLDER'], 'form_data.xlsx')
                generate_excel(form_data, excel_path)
                
                return render_template('index.html', json_file=json_output_path, excel_file=excel_path)
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
