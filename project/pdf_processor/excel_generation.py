import openpyxl

def generate_excel(form_data, excel_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Form Data"

    # Write headers
    sheet.append(["Label", "Type", "Custom Label", "Value"])

    # Write form data
    for field in form_data.values():
        label = field['label']
        field_type = field['type']
        customLabel = field['customLabel']
        value = field['value']
        sheet.append([label, field_type, customLabel, value])

    # Save the workbook
    workbook.save(excel_path)
