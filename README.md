# 🧬 BioBridge: Precision Biomarker Extraction & RAG Pipeline

**BioBridge** is an end-to-end automated pipeline designed to transform unstructured medical PDFs into a structured, queryable knowledge base. By moving beyond naive RAG chunking, BioBridge uses a multi-layered verification strategy to extract high-fidelity statistical data from clinical research.

## 🚀 The Pipeline Flow

### 1. Data Ingestion & Structuring
*   **PDF-to-HTML Conversion:** Ingests raw research papers and converts them into HTML to preserve document hierarchy, table structures, and section boundaries.
*   **Hierarchical JSON Parsing:** Parses the HTML into a structured JSON format where keys represent **Headings** and values are **Paragraph Lists**. This ensures the system understands whether a sentence belongs to the *Methods*, *Results*, or *Discussion* section.

### 2. Entity Discovery
*   **Biomarker Identification:** Scans the text to identify specific biological markers (e.g., Lymphocyte count, Procalcitonin).
*   **Population Profiling:** Extracts critical study demographics, including total sample size ($N$), clinical conditions (e.g., Sepsis-3), and geographic location.

### 3. Precision Retrieval Engine
To solve the "garbage in, garbage out" problem in standard RAG, BioBridge employs a **Contextual Guardrail System**:
*   **Keyword & Semantic Hybrid Search:** Identifies exact biomarker matches and utilizes **Sentence Subject Matching** to define the ideal context window.
*   **Heuristic Validation:** Uses **Cosine Similarity** against a specialized **Control Text** to score extracted windows. This filters out background discussion and focuses exclusively on text containing raw findings and methodology.

### 4. Synthesis & Intelligence
*   **Structured Summarization:** Relevant context is passed to a Large Language Model (LLM) to transform dense prose into a concise, tabular summary containing:
    *   Effect Size (Odds Ratios, Cutoffs)
    *   Performance Metrics (AUC, Sensitivity, Specificity)
*   **Vectorized Knowledge Base:** All structured findings are stored in a **Vector Database**.
*   **Real-time RAG:** A Retrieval-Augmented Generation interface allows users to ask complex natural language questions and receive answers grounded strictly in the validated research data.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **LLM** | Gemini 1.5 Flash / Pro |
| **Embeddings** | `text-embedding-004` |
| **Data Format** | HTML ➔ JSON |
| **Vector DB** | ChromaDB / Pinecone |

---

## 💡 Key Innovation: "The Relevance Guardrail"
Standard RAG systems often retrieve irrelevant text that "looks" similar but contains no data. Our innovation lies in the **Control Text Heuristic**. By measuring how close a text block is to a "Statistical Results" anchor, we effectively silence the noise of the *Introduction* and *Bibliography*, ensuring the LLM only synthesizes the most impactful data points.

---

## 📖 Example Output
| Biomarker | Population | AUC | Effect Size |
| :--- | :--- | :--- | :--- |
| Lymphocyte Count | 385 (Sepsis, Japan) | 0.78 | Cutoff: $0.8 \times 10^9$ |

---

## 🏁 Getting Started
1. Clone the repository.
2. Add your API keys to `.env`.
3. Run `python main.py --ingest [path_to_pdf]`.
4. Query the knowledge base via the CLI or UI.
