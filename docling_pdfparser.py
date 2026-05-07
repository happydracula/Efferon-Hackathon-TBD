import warnings
warnings.filterwarnings('ignore')

import re
import pandas as pd
import os
from tqdm import tqdm
from docling.document_converter import DocumentConverter

for file in tqdm(os.listdir('./articles/')):
    filepath = './articles/'+file
    filename = file.split('.')[0]
    
    if '.pdf' not in filepath:
        continue
        
    converter = DocumentConverter()
    result = converter.convert(filepath)
    doc = result.document

    markdown = doc.export_to_markdown()

    with open(f"./docling_outputs/{filename}.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    