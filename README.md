.

🔬 Project Overview: Precision Bio-Marker Extraction & RAG
This project implements an automated pipeline designed to ingest complex medical research papers and extract structured insights regarding biomarkers and study populations. Unlike standard RAG implementations that rely on naive chunking, this system uses a multi-stage heuristic and semantic filtering process to ensure high data fidelity.

🏗️ Technical Architecture
1. Data Transformation & Structuring
Ingestion & Normalization: Source PDFs are converted into HTML, preserving the structural integrity of the document (headings, tables, and paragraphs).

Schema-Aware Parsing: The HTML is transformed into a Structured JSON format, mapping specific section headings to their respective paragraph lists. This allows the system to maintain sectional context (e.g., distinguishing "Methods" from "Discussion").

2. Intelligent Entity Identification
Biomarker & Population Discovery: The system automatically identifies the specific biomarkers and population demographics (e.g., Sepsis-3, N-counts, geographic location) targeted in the research.

3. Contextual Retrieval Engine (The "Precision" Layer)
To find the most relevant evidence for each biomarker, we employ a triple-filtering approach:

Exact Match: Keyword-based searching for direct mentions.

Semantic Windowing: Using Cosine Similarity and Sentence Subject Matching to dynamically define the context window around a hit, ensuring the extracted text is semantically complete.

Control-Text Validation: Extracted windows are validated against a "control text" using cosine similarity and heuristic measures to filter out "noise" (e.g., brief mentions in the bibliography vs. actual results).

4. LLM Synthesis & Real-Time Querying
Structured Summarization: Relevant context windows are fed into a Large Language Model (LLM) to synthesize findings into a concise, tabular format (e.g., Effect Size, Performance, AUC, and Sensitivity).

Vector DB & RAG: All extracted data and summaries are stored in a Vector Database, enabling real-time, natural language queries over the entire research corpus.

🛠️ Tech Stack
Language: Python

Embedding Model: google/gemini-embedding-001 (or your chosen model)

LLM: Gemini 1.5 Flash / Pro

Vector Database: (e.g., Pinecone, ChromaDB, or Weaviate)

Parsing: HTML/JSON Custom Parser
