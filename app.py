from data_extraction_pipeline.extract_schema import extract_schema
import json
from tqdm import tqdm
import os
with open('./data/articles_json/Baloch_2022.html_extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    extract_schema(data, f.name)


files = [f for f in os.listdir("./data/articles_json/") if f.endswith('.html')]
for file in tqdm(files, desc="Extracting insights"):
    with open(f"./data/articles_json/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
        extracted_insights = extract_schema(data, f.name)
        print(extracted_insights)
        #TODO: Save to DB