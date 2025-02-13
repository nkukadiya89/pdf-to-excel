import datetime
import os

import pandas as pd
import pdfplumber
from flask import Blueprint, jsonify, render_template, request, send_file

upload_blueprint = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def delete_old_files():
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(minutes=1)
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            if timestamp < cutoff:
                os.remove(filepath)

@upload_blueprint.route("/upload_bs", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        delete_old_files()
        file = request.files["file"]
        if file.filename.endswith(".pdf"):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Convert PDF to Excel
            excel_path = convert_pdf_to_excel(filepath)

            # Remove the uploaded PDF file after conversion
            os.remove(filepath)

            # Return success message and file name
            return jsonify({"success": True, "file_path": excel_path})

    return render_template("upload.html")

@upload_blueprint.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        response = send_file(file_path, as_attachment=True)
        return response
    return "File not found", 404

def convert_pdf_to_excel(pdf_path):
    extracted_data = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table)
                df.reset_index(drop=True, inplace=True)  # Reset index after dropping
                if len(df.columns) >= 3:  # Ensure B and C columns exist
                    df = df.dropna(subset=[1, 2])  # Drop rows where column B (index 1) or C (index 2) is empty
                extracted_data[f"Sheet_{i+1}"] = df

    excel_path = pdf_path.replace(".pdf", ".xlsx")
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_name, df in extracted_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return excel_path