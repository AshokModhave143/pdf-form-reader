# PDF Form Reader

This project reads the pdf forms and output the key and value to excel file

## Sample PDFs

- https://www.irs.gov/pub/irs-pdf/fw9.pdf
- https://www.irs.gov/pub/irs-pdf/fw8ben.pdf

## Generate mapping

```sh
python3 ./src/pdf-processor.py input/fw8ben.pdf --prepare-json
```

## Run program

```sh
python3 ./src/pdf-processor.py input/fw8ben.pdf output/fw8ben.xlsx
```
