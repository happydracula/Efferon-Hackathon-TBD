from nlp_utils import get_cosine_similarity, get_combined_embedding, get_subject_of_sentence, get_meaningful_words, get_sentences_from_para
from llm_invoker import get_embedding, call_llm
from data_extraction_pipeline.extract_findings import extract_core_findings
import json
from prompts import RESEARCH_EXTRACTION_PROMPT


SCHEMA = ["Study", "Population", "Sample Size", "Predictor", "Outcome", "Timing", "Method",
          "Effect Size", "Performance", "Notes", "Source"]

def extract_relevant_context_for_findings(paragraph_dicts, search_terms, sim_threshold=0.6, overlap_threshold=1.0):
    extracted_results = []
    embedding_cache = {}

    def get_cached_emb(text):
        if text not in embedding_cache:
            embedding_cache[text] = get_embedding(text)
        return embedding_cache[text]

    # Iterate through the list of dictionaries from your flattened JSON
    for item in paragraph_dicts:
        title = item['title']
        raw_text = item['text']
        
        # Split the text into sentences for granular analysis
        sentences = get_sentences_from_para(raw_text)

        visited_indices = set()
        
        # Find seeds: sentences containing search terms (or if the title itself is a match)
        seeds = [i for i, sent in enumerate(sentences) 
                 if any(term.lower() in sent.lower() for term in search_terms) or 
                    any(term.lower() in title.lower() for term in search_terms)]
        
        for seed_idx in seeds:
            if seed_idx in visited_indices:
                continue
            
            current_block_indices = [seed_idx]
            
            # --- Expand Backwards ---
            ptr = seed_idx - 1
            while ptr >= 0:
                avg_emb = get_combined_embedding(sentences, current_block_indices)
                candidate_emb = get_cached_emb(sentences[ptr])
                
                sim = get_cosine_similarity(avg_emb, candidate_emb)
                
                # Check lexical overlap
                w_neighbor = get_meaningful_words(sentences[ptr+1])
                w_candidate = get_meaningful_words(sentences[ptr])
                overlap = len(w_neighbor & w_candidate) / max(len(w_neighbor | w_candidate), 1)

                # Expansion condition
                if overlap > overlap_threshold or sim > sim_threshold:
                    current_block_indices.insert(0, ptr)
                    ptr -= 1
                else:
                    break

            # --- Expand Forwards ---
            ptr = seed_idx + 1
            while ptr < len(sentences):
                # Using your new subject-checking logic
                next_subjects = get_subject_of_sentence(sentences[ptr])
                subjects_str = " ".join(next_subjects).lower()
                
                # Expand if the subject matches a search term OR is semantically similar
                if any(term.lower() in subjects_str for term in search_terms):
                    current_block_indices.append(ptr)   
                    ptr += 1
                else:
                    # Optional: Add a small similarity check for forward expansion too
                    avg_emb = get_combined_embedding(sentences, current_block_indices)
                    if get_cosine_similarity(avg_emb, get_cached_emb(sentences[ptr])) > sim_threshold + 0.1:
                         current_block_indices.append(ptr)
                         ptr += 1
                    else:
                        break

            # Create the final block and keep the title metadata
            final_text = " ".join([sentences[i] for i in current_block_indices])
            extracted_results.append({
                "title": title,
                "relevant_text": final_text,
                "search_terms_found": [t for t in search_terms if t.lower() in final_text.lower() or t.lower() in title.lower()]
            })
            
            visited_indices.update(current_block_indices)

    return extracted_results

def flatten_document_structure(structured_data):
    """
    Inverts a hierarchical JSON into a flat list of dictionaries.
    Each dictionary contains 'title' and 'text'.
    """
    flattened_list = []

    for main_header, content in structured_data.items():
        # Case 1: Section has no sub-headers (Content is a List)
        if isinstance(content, list):
            for paragraph in content:
                flattened_list.append({
                    "title": main_header,
                    "text": paragraph
                })
        
        # Case 2: Section has sub-headers (Content is a Dictionary)
        elif isinstance(content, dict):
            for sub_header, paragraphs in content.items():
                # Construct a combined title for context
                # If sub_header is 'General', we just use the main_header name
                if sub_header == "General":
                    display_title = main_header
                else:
                    display_title = f"{main_header} - {sub_header}"
                
                # Iterate through the list of paragraphs under this sub-header
                for paragraph in paragraphs:
                    flattened_list.append({
                        "title": display_title,
                        "text": paragraph
                    })
                    
    return flattened_list

def summarize_context_into_schema(relevant_context, article_title):
    """
    Synthesizes extracted evidence blocks into the final research schema.
    """
    # 1. Combine all evidence into a single string with source headers
    full_evidence = ""
    for entry in relevant_context:
        full_evidence += f"\n[Section: {entry['title']}]\n{entry['relevant_text']}\n"

    # 2. Call the LLM (using your preferred client, e.g., OpenAI or Anthropic)
    # The prompt is defined below
    prompt = f"""
    {RESEARCH_EXTRACTION_PROMPT}
    
    SOURCE MATERIAL:
    {full_evidence}
    
    METADATA:
    Original Article: {article_title}
    """
    
    # Assuming call_llm() is your interface to the model
    response_text = call_llm(prompt) 
    
    try:
        # Parse the JSON response from the LLM
        summarized = json.loads(response_text)
    except:
        # Fallback if LLM returns text instead of JSON
        summarized = {key: "Extraction Failed" for key in SCHEMA}
    return summarized




#TODO: Improve this logic
def get_population_summary(abstract_text: str):
    
    prompt = f"""
    Based on the following research abstract text, provide a single, concise summary 
    sentence of the study population. 
    Include the total N, the condition (e.g., Sepsis-3), and the location if mentioned.
    
    Abstract: {abstract_text}
    
    Summary:
    """
    response = call_llm(prompt)
    return response


def extract_schema(article_json, filename):
    inverted_document = flatten_document_structure(article_json)
    core_findings = extract_core_findings(article_json["Abstract"])
    population_summary = get_population_summary(article_json["Abstract"])
    schema_objects = []
    for key_term in core_findings["biomarkers"]:
        summarized_finding = {"Study":filename}
        terms = [key_term["canonical_name"]] + key_term["synonyms"]
        relevant_context = extract_relevant_context_for_findings(inverted_document, terms)
        print(f"Key Term: {key_term['canonical_term']}")
        print(f"Relevant Context: {relevant_context}")
        print("-" * 50)
        summarized_finding.update(summarize_context_into_schema(relevant_context))
        print(f"Summarized Finding: {summarized_finding}")
        if not summarized_finding["Population"]:
            summarized_finding["Population"] = population_summary
        schema_objects.append(summarized_finding)
    return schema_objects
