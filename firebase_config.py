
  
  #imports
  #firebase config
  #read json files from output folder
  #for each file, read the json data
    #for each json data, push to firebase


import os
import json
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase with Application Default Credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'yourskills-pro',
    'storageBucket': 'yourskills-pro.appspot.com'
})

db = firestore.client()

def upload_to_experts(category: str, data: Dict[str, Any]) -> None:
    """Upload CV data to experts collection"""
    try:
        # Create document in talents collection
        doc_ref = db.collection('Talents').document()
        
        # Add metadata
        data['category'] = category
        data['uploadedAt'] = firestore.SERVER_TIMESTAMP
        
        # Upload data
        doc_ref.set(data)
        print(f"✅ Uploaded: {data['name']} to talents collection")
        
    except Exception as e:
        print(f"❌ Error uploading {data.get('name', 'Unknown')}: {str(e)}")

def process_json_files():
    """Process JSON files and upload to Firestore"""
    output_dir = "output"
    
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            category = filename.replace('.json', '')
            
            print(f"\nProcessing category: {category}")
            with open(os.path.join(output_dir, filename), 'r') as f:
                cv_data_list = json.load(f)
                
            for cv_data in cv_data_list:
                upload_to_experts(category, cv_data)

def main():
    try:
        process_json_files()
        print("\nData upload complete!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()