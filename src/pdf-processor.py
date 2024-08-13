import PyPDF2
import pdfplumber
import json
import sys
import openpyxl

# Custom label mapping
CUSTOM_LABELS = {
    # "f_1[0]": "NAME_OF_INDIVIDUAL",
    # "f_2[0]": "COUNTRY_OF_CITIZENSHIP",
    # "f_3[0]": "ADDRESS",
    # "f_4[0]": "CITY"
}


def extract_form_fields(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        fields = reader.get_fields()

        form_data = {}
        if fields:
            for field_key, field_value in fields.items():
                field_name = field_key
                field_type = field_value.get('/FT')
                field_data = field_value.get('/V', '')

                if field_type == '/Btn':
                    if '/AS' in field_value:
                        field_data = 'Checked' if field_value['/AS'] != '/Off' else 'Unchecked'
                    else:
                        field_data = 'Unchecked'

                label = CUSTOM_LABELS.get(field_name, field_value.get('/T', ''))
                form_data[field_name] = {
                    'value': field_data,
                    'type': field_type,
                    'label': label
                }
        return form_data

def extract_text_from_pdf(pdf_path):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data.append(page.extract_text())
    return "\n".join(text_data)

def generate_excel(form_data, excel_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Form Data"

    # Write headers
    sheet.append(["Label", "Value"])

    # Write form data
    for field in form_data.values():
        label = field['label']
        value = field['value']
        sheet.append([label, value])

    # Save the workbook
    workbook.save(excel_path)

def main(pdf_path, excel_path):
    form_data = extract_form_fields(pdf_path)
    # text_data = extract_text_from_pdf(pdf_path)
    
    result = {
        'form_fields': form_data,
        # 'text_content': text_data
    }

    json_output = json.dumps(result, indent=4)
    print(json_output)

    # Generate Excel file
    generate_excel(form_data, excel_path)
    print(f"Excel file saved to {excel_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_pdf>")
    else:
        pdf_path = sys.argv[1]
        excel_path = sys.argv[2]
        main(pdf_path, excel_path)
