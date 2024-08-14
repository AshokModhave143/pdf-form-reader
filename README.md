# PDF Form Reader

This project reads the pdf forms and output the key and value to excel file

## Sample PDFs

- https://www.irs.gov/pub/irs-pdf/fw9.pdf
- https://www.irs.gov/pub/irs-pdf/fw8ben.pdf

## Pre-requisites

- Python3 installed

## Libraries used

- Python3
- PyPDF2
- openpxl
- flask
- pdfplumber

## Get started

### Folders

```yaml
pdf-form-reader
- input
- output
- mappings
- project
- .gitignore
- README.md
- requirements.txt
```

### Setting up virual environment

```bash
cd pdf-form-reader
python3 -m venv venv
source venv/bin/activate
```

### Installing dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Generate mapping

```bash
python3 project/main.py input/fw8ben.pdf --prepare-json
```

## Run project

### Command line

```bash
python3 project/main.py input/fw8ben.pdf output/fw8ben.xlsx
```

### Render UI

```bash
export FLASK_APP=project/web/app.py
flask run
```

## Accessing UI

Above command will run the application and you can access it at `http://127.0.0.1:5000`
