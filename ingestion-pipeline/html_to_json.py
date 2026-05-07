import json
import os
from bs4 import BeautifulSoup
import re

from tqdm import tqdm

def is_subheading(tag, current_main_tag):
    if not current_main_tag:
        return False
    text = tag.get_text().strip()
    if not text: return False
    
    # 1. Lower Header Level Check (h3 > h2)
    # Using .get() to avoid index errors if tag is just 'p'
    tag_level = int(re.search(r'\d+', tag.name).group()) if tag.name.startswith('h') else 9
    main_level = int(re.search(r'\d+', current_main_tag.name).group()) if current_main_tag.name.startswith('h') else 0
    
    if tag.name.startswith('h') and tag_level > main_level:
        return True

    # 2. Numbering Check (1.1, 2.1)
    if re.match(r'^\d+(\.\d+)+', text):
        return True

    # 3. Casing Shift (ALL CAPS -> Title Case)
    if current_main_tag.get_text().strip().isupper():
        if not text.isupper() and len(text.split()) < 10:
            return True

    return False

def parse_html_to_hierarchy(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    structured_data = {}
    
    # Initialize state with a fallback for text before any headers
    current_main_str = "Front_Matter"
    current_main_tag = None 
    current_sub_str = None
    
    structured_data[current_main_str] = []

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
        text = element.get_text().strip()
        if not text: continue

        # --- Main Header Detection ---
        if element.name in ['h1', 'h2']:
            current_main_tag = element
            current_main_str = text
            current_sub_str = None
            if current_main_str not in structured_data:
                structured_data[current_main_str] = []
        
        # --- Sub-Header Detection ---
        elif is_subheading(element, current_main_tag):
            current_sub_str = text
            
            # If the main section was a list, convert it to a dict to hold sub-sections
            if isinstance(structured_data[current_main_str], list):
                existing_content = structured_data[current_main_str]
                structured_data[current_main_str] = {"General": existing_content}
            
            if current_sub_str not in structured_data[current_main_str]:
                structured_data[current_main_str][current_sub_str] = []

        # --- Paragraph Collection ---
        elif element.name == 'p':
            if current_sub_str:
                # We are inside a sub-section
                structured_data[current_main_str][current_sub_str].append(text)
            else:
                # We are in the main section (e.g., Intro) but no sub-section yet
                if isinstance(structured_data[current_main_str], dict):
                    structured_data[current_main_str]["General"].append(text)
                else:
                    structured_data[current_main_str].append(text)

    return structured_data

# --- Usage remains the same ---
files = [f for f in os.listdir("./data/articles_html/") if f.endswith('.html')]
for file in tqdm(files, desc="Parsing HTML"):
    with open(f"./data/articles_html/{file}", "r", encoding="utf-8") as f:
        html_data = f.read()
        result_json = parse_html_to_hierarchy(html_data)
        with open(f"./data/articles_json/{file}_extracted.json", "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=4)