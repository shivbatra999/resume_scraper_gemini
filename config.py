
import os
# 🔹 Configuration file for API keys and settings
GEMINI_API_KEY = ""


# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RESUMES_FOLDER = os.path.join(BASE_DIR, "resumes")

# Output file path
OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, "extracted_data.xlsx")
