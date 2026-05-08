from data_extraction_pipeline.extract_schema import extract_schema
import json
from tqdm import tqdm
import os
from data_query_system.ingest_schema import ingest_data

files = [f for f in os.listdir("../data/articles_json/") if f.endswith('.json')]
for file in tqdm(files, desc="Extracting insights"):
    with open(f"../data/articles_json/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
        extracted_insights = extract_schema(data, f.name)
        for insight in extracted_insights:
            ingest_data(insight)