import os
import json
import time
import logging
import re
from typing import Dict, Any
from datetime import datetime
import pytz
import google.generativeai as genai
from config import GEMINI_API_KEY, OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format='%(message)s')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

TIMESTAMP = datetime.now(pytz.timezone('US/Central')).replace(
    hour=15, minute=0, second=0, microsecond=0
).isoformat()

def extract_cv_data(cv_text: str) -> Dict[str, Any]:
    prompt = f"""Extract CV information as CLEAN JSON with exactly this structure:
    {{
        "Bio": "2-3 sentence professional summary",
        "email": "email from CV",
        "experience_years": "total years of experience",
        "job_title": "current job title",
        "location": "city, country from CV",
        "name": "full name from CV",
        "skills": [
            {{
                "name": "skill name",
                "rating": 3
            }}
        ],
        "social": {{
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }}
    }}

    Rules:
    1. Extract exactly 10 key technical skills
    2. Rate each skill 1-3 (3=expert, 2=intermediate, 1=basic)
    3. Use empty string "" for missing values 
    4. Never return null values
    5. Return only valid JSON
    6. Do not include any prefixes like 'json' or 'JSON'

    CV Text:
    {cv_text}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"\nExtracting data (attempt {attempt + 1})...")
            response = model.generate_content(prompt)
            time.sleep(2 ** attempt)
            
            if not response or not response.text:
                raise ValueError("Empty response")
                
            # Clean response text
            text = response.text.strip()
            
            # Remove any prefixes/suffixes and get JSON block
            if '```' in text:
                blocks = text.split('```')
                for block in blocks:
                    if '{' in block and '}' in block:
                        text = block.strip()
                        break
            
            # Remove common prefixes
            text = re.sub(r'^(json|JSON)', '', text)
            text = re.sub(r'^.*?{', '{', text)
            text = re.sub(r'}.*$', '}', text)
            
            # Clean up JSON content
            text = re.sub(r'[\x00-\x1F\x7F]', '', text)
            text = re.sub(r'//.*?(\r\n|\r|\n|$)', '', text)
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            text = text.replace('null', '""')
            text = text.replace('\n', ' ').replace('\r', '')
            
            # Fix truncated URLs in social links
            text = re.sub(r'"linkedin":\s*"https?:(?!")', r'"linkedin": "', text)
            text = re.sub(r'"github":\s*"https?:(?!")', r'"github": "', text)
            text = re.sub(r'"portfolio":\s*"https?:(?!")', r'"portfolio": "', text)
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # Additional cleanup for problematic JSON
                text = re.sub(r'[^\x20-\x7E]', '', text)
                text = re.sub(r',\s*([\]}])', r'\1', text)
                data = json.loads(text)
            
            # Validate and clean data
            for field in ['Bio', 'email', 'experience_years', 'job_title', 'location', 'name']:
                if field not in data or data[field] is None:
                    data[field] = ""
            
            # Format skills (limit to 10)
            if 'skills' in data:
                formatted_skills = []
                for skill in data['skills'][:10]:
                    if isinstance(skill, dict) and 'name' in skill:
                        rating = min(max(int(skill.get('rating', 1)), 1), 3)
                        formatted_skills.append({
                            'name': skill['name'].strip(),
                            'rating': rating
                        })
                data['skills'] = formatted_skills
            
            # Ensure social links
            if 'social' not in data:
                data['social'] = {'linkedin': '', 'github': '', 'portfolio': ''}
            
            data['timestamp'] = TIMESTAMP
            print(f"Successfully parsed JSON for {data.get('name', 'Unknown')}")
            return data
            
        except Exception as e:
            print(f"❌ Error (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                print("Failed after max retries, attempting emergency parsing...")
                try:
                    # Emergency parse - grab what we can
                    emergency_data = {
                        "Bio": "",
                        "email": "",
                        "experience_years": "",
                        "job_title": "",
                        "location": "",
                        "name": "",
                        "skills": [],
                        "social": {"linkedin": "", "github": "", "portfolio": ""},
                        "timestamp": TIMESTAMP
                    }
                    
                    # Try to extract name and email using regex
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
                    if email_match:
                        emergency_data["email"] = email_match.group()
                    
                    return emergency_data
                except:
                    print("Emergency parsing failed")
                    return None
    
    return None

# ...rest of existing code...

def process_and_save(category_dir: str, filename: str, output_file: str) -> bool:
    filepath = os.path.join(category_dir, filename)
    print(f"\n{'='*50}")
    print(f"Processing: {filename}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cv_text = f.read()
            
        data = extract_cv_data(cv_text)
        if not data:
            return False
            
        data['filename'] = filename
        data['category'] = os.path.basename(category_dir)
        
        existing = []
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                
        existing.append(data)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)
            
        print(f"✅ Successfully processed and saved {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {str(e)}")
        return False

def main():
    base_dir = "textresume"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get and sort categories
    categories = [d for d in os.listdir(base_dir) 
                 if os.path.isdir(os.path.join(base_dir, d))]
    categories.sort(key=lambda x: int(re.search(r'\d+', x).group() or 0))
    
    for category in categories:
        category_dir = os.path.join(base_dir, category)
        print(f"\nProcessing category: {category}")
        output_file = os.path.join(OUTPUT_DIR, f"{category}.json")
        
        # Get and sort files numerically
        files = [f for f in os.listdir(category_dir) if f.endswith('.txt')]
        files.sort(key=lambda x: int(re.search(r'\d+', x).group() or 0))
        
        for filename in files:
            process_and_save(category_dir, filename, output_file)

if __name__ == "__main__":
    main()