import os
from PyPDF2 import PdfReader
from markdownify import markdownify as md
from config import RESUMES_FOLDER

def convert_pdfs_to_text(input_folder=RESUMES_FOLDER, output_folder="textresume"):
    """Convert all PDFs to text files preserving folder structure"""
    
    for root, dirs, files in os.walk(input_folder):
        # Get relative path to maintain folder structure
        rel_path = os.path.relpath(root, input_folder)
        
        # Create corresponding output directory
        if rel_path != ".":
            output_path = os.path.join(output_folder, rel_path)
            os.makedirs(output_path, exist_ok=True)
        else:
            output_path = output_folder
            os.makedirs(output_path, exist_ok=True)
            
        # Process PDF files
        for pdf_file in files:
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(root, pdf_file)
                text_file = os.path.join(output_path, f"{os.path.splitext(pdf_file)[0]}.txt")
                
                try:
                    reader = PdfReader(pdf_path)
                    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                    
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                        
                    print(f"Converted: {pdf_file}")
                except Exception as e:
                    print(f"Error processing {pdf_file}: {str(e)}")

if __name__ == "__main__":
    convert_pdfs_to_text()