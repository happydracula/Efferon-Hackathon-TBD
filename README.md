This project is an end-to-end automated pipeline designed to transform unstructured medical PDFs into a structured, queryable knowledge base.

##  The Pipeline Flow

### 1. Data Ingestion & Structuring
*   **PDF-to-HTML Conversion:** Ingests raw research papers and converts them into HTML using docling
*   **Hierarchical JSON Parsing:** Parses the HTML into a structured JSON format where keys represent **Headings** and values are **Paragraph Lists**. This ensures the system understands whether a sentence belongs to the *Methods*, *Results*, or *Discussion* section.

### 2. Entity Discovery
*   **Biomarker Identification:** Scans the text to identify specific biological markers (e.g., Lymphocyte count, Procalcitonin).
*   **Population Profiling:** Extracts critical study demographics, including total sample size ($N$), clinical conditions (e.g., Sepsis-3), and geographic location.

### 3. Context Retrieval 
*   **Keyword & Semantic Hybrid Search:** Identifies exact keyword matches to identify potentially relevant sentences. Since a single sentence may not hold all the necessary information, **cosine similarity** and **sentence subject matching** are used to expand the context window to later and previous sentences.
*   **Heuristic Validation:** Uses **Cosine Similarity** against a specialized **Control Text** to extract only relevant windows. This filters out background discussion and focuses exclusively on text containing raw findings and methodology.

### 4. Synthesis & Intelligence
*   **Structured Summarization:** Relevant context is passed to a Large Language Model (LLM) to transform dense prose into a concise, tabular summary.
*   **Vectorized Knowledge Base:** All structured findings are stored in a **Vector Database**.
*   **Real-time RAG:** A Retrieval-Augmented Generation interface allows users to ask complex natural language questions and receive answers grounded strictly in the validated research data.
  
## Data Querying 

### 1. Data Storage (PostgreSQL + pgvector)
We store the extracted clinical information in a PostgreSQL database. Instead of just saving text, we store embeddings of specific columns to enable natural-language querying of evidence and conclusions.

### 2. Querying with Cosine Similarity
When a user asks a question, we perform a cosine similarity of the query vector against the database columns to extract relevant documents ranked by their relevance.
