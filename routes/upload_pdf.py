import os
import re

import pandas as pd
import pdfplumber
from flask import Blueprint, render_template, request, send_file

upload_pdf_blueprint = Blueprint('upload_pdf', __name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return filename.endswith('.pdf')

def is_date(value):
    """Check if a string is in date format (e.g., 'JUN14', 'JUL23')."""
    return bool(re.match(r"^[A-Z]{3}\d{2}$", value))  # Matches formats like "JUN14"

def extract_table_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        data = [line.split() for line in text.split("\n") if len(line.split()) > 1]

    if not data:
        return None

    # Filter rows where the first column matches the date format
    filtered_data = [row[:4] for row in data if is_date(row[0])]  # Get only A, B, C, D columns
    return pd.DataFrame(filtered_data, columns=["A", "B", "C", "D"]) if filtered_data else None

@upload_pdf_blueprint.route('/format_1')
def index():
    return render_template('upload_pdf.html')

@upload_pdf_blueprint.route('/upload_pdf', methods=['POST'])
def upload_pdf_file():
    file = request.files.get('file')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return 'Invalid file. Please upload a PDF.', 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = extract_table_from_pdf(filepath)
    if df is None:
        return 'No table detected in the uploaded PDF.', 400

    excel_filepath = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(file.filename)[0]}.xlsx")
    try:
        df.to_excel(excel_filepath, index=False)
        return send_file(excel_filepath, as_attachment=True)
    except Exception as e:
        return f"Error exporting to Excel: {e}", 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
