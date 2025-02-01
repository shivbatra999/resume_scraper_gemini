import gdown
import zipfile
import os
from config import RESUMES_FOLDER

def validate_folder(output_folder):
    """Validates if folder exists and is writable."""
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except OSError as e:
            raise ValueError(f"Could not create output folder: {e}")
    if not os.access(output_folder, os.W_OK):
        raise ValueError(f"Output folder {output_folder} is not writable")

def get_folder_id(url):
    """Extract folder ID from Google Drive URL"""
    if "folders/" in url:
        return url.split("folders/")[1].split("?")[0]
    return url

def download_and_extract(folder_url):
    folder_id = get_folder_id(folder_url)
    try:
        success = gdown.download_folder(
            id=folder_id,
            output=RESUMES_FOLDER,
            quiet=False
        )
        return success
    except Exception as e:
        print(f"Download error: {str(e)}")
        return False