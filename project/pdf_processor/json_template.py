import PyPDF2
import json
import os

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

def prepare_json_template_data(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        fields = reader.get_fields()

        template_data = {}
        if fields:
            for field_key, field_value in fields.items():
                field_label = field_value.get('/T', field_key)
                template_data[field_label] = ""

    return template_data
