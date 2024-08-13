import PyPDF2
import json
import sys
import os

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

def extract_form_fields(pdf_path, custom_labels):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        fields = reader.get_fields()

        form_data = {}
        if fields:
            for field_key, field_value in fields.items():
                field_name = field_key
                field_type = field_value.get('/FT')
                field_data = field_value.get('/V', '')
                field_label = field_value.get('/T', field_name)

                # Correctly handle checkbox values
                if field_type == '/Btn':
                    if field_value.get('/V') == '/1':
                        field_data = 'Checked'
                    else:
                        field_data = 'Unchecked'
                    field_type = 'checkbox'
                elif field_type == '/Tx':
                    field_type = 'input'
                elif field_type == '/Ch':
                    field_type = 'textarea'
                else:
                    field_type = 'unknown'

                custom_label = custom_labels.get(field_label, '')
                form_data[field_name] = {
                    'value': field_data,
                    'type': field_type,
                    'label': field_label,
                    'customLabel': custom_label
                }
        return form_data

def generate_excel(form_data, excel_path):
    import openpyxl
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Form Data"

    # Write headers
    sheet.append(["Label","Type", "Custom Label", "Value"])

    # Write form data
    for field in form_data.values():
        label = field['label']
        field_type = field['type']
        customLabel = field['customLabel']
        value = field['value']
        sheet.append([label, field_type, customLabel, value])

    # Save the workbook
    workbook.save(excel_path)

def prepare_json_template(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        fields = reader.get_fields()

        if fields:
            template_data = {}
            for field_key, field_value in fields.items():
                field_label = field_value.get('/T', field_key)
                template_data[field_label] = ""

            # Ensure mappings folder exists
            os.makedirs("mappings", exist_ok=True)

            # Save template JSON file in mappings folder
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            json_template_path = os.path.join("mappings", f"{base_name}.json")
            with open(json_template_path, 'w') as json_file:
                json.dump(template_data, json_file, indent=4)
            
            print(f"Template JSON file saved to {json_template_path}")
        else:
            print("No form fields found in the PDF.")

def main(pdf_path, excel_path=None, prepare_json=False):
    if prepare_json:
        prepare_json_template(pdf_path)
    else:
        custom_labels = load_custom_labels(pdf_path)
        form_data = extract_form_fields(pdf_path, custom_labels)

        result = {
            'form_fields': form_data,
        }
        json_output = json.dumps(result, indent=4)
        print(json_output)

        if excel_path:
            generate_excel(form_data, excel_path)
            print(f"Excel file saved to {excel_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python script.py <path_to_pdf> [<path_to_excel>] [--prepare-json]")
    else:
        pdf_path = sys.argv[1]
        excel_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
        prepare_json = '--prepare-json' in sys.argv

        main(pdf_path, excel_path, prepare_json)
