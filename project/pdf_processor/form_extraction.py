import PyPDF2

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
                    if field_value.get('/V') == '/1' or field_value.get('/V') == '/Yes' or field_value.get('/V') == '/On':
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
