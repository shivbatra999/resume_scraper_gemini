from google_drive_utils import download_and_extract
from pdf_to_text import process_all_pdfs
from gemini_extraction import extract_fields_with_gemini
from save_to_excel import save_to_excel

if __name__ == "__main__":
    drive_link = input("Enter Google Drive Folder Link: ")

    # Step 1: Download & Extract PDFs
    download_and_extract(drive_link)

    # Step 2: Extract Text from PDFs
    extracted_texts = process_all_pdfs()

    # Step 3: Process CVs with Gemini AI
    structured_data = [extract_fields_with_gemini(text) for text in extracted_texts.values()]

    # Step 4: Save Extracted Data to Excel
    save_to_excel(structured_data)
