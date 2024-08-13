import sys
import json

# from pdf_processor.custom_labels import load_custom_labels
# from pdf_processor.form_extraction import extract_form_fields
# from pdf_processor.excel_generation import generate_excel
# from pdf_processor.json_template import prepare_json_template

from pdf_processor import load_custom_labels, prepare_json_template, generate_excel, extract_form_fields

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
        print("Usage: python main.py <path_to_pdf> [<path_to_excel>] [--prepare-json]")
    else:
        pdf_path = sys.argv[1]
        excel_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
        prepare_json = '--prepare-json' in sys.argv

        main(pdf_path, excel_path, prepare_json)
