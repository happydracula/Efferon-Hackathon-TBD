import os
from tqdm import tqdm
from docling.document_converter import DocumentConverter
import json
# 1. Create the output directory if it doesn't exist
output_dir = "Efferon-Hackathon-TBD/data/articles_html/"
os.makedirs(output_dir, exist_ok=True)

# 2. Initialize the converter ONCE outside the loop (saves RAM and Time)
converter = DocumentConverter()

# 3. Get list of files
input_dir = 'Efferon-Hackathon-TBD/data/articles/'
files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]

for file in tqdm(files, desc="Parsing PDFs"):
    filepath = os.path.join(input_dir, file)
    filename = os.path.splitext(file)[0]
    
    try:
        # Convert the document
        result = converter.convert(filepath)
        doc = result.document

        # Export to dictionary
        doc_dict = doc.export_to_html()

        # Save to the parsed_articles directory
        output_path = os.path.join(output_dir, f"{filename}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(doc_dict)
            
    except Exception as e:
        print(f"Error processing {file}: {e}")

