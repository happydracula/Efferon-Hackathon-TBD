import math
from llm_invoker import get_embedding
import spacy

nlp = spacy.load("en_core_web_sm")
def get_cosine_similarity(v1, v2):
    dot_product = sum(x * y for x, y in zip(v1, v2))
    mag1 = math.sqrt(sum(x**2 for x in v1))
    mag2 = math.sqrt(sum(x**2 for x in v2))
    return dot_product / (mag1 * mag2) if (mag1 * mag2) > 0 else 0

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", 
    "is", "are", "was", "were", "of", "from", "by", "it", "this", "that", "these", "those"
}

def get_meaningful_words(text):
    """Filters out stop words and punctuation-heavy noise."""
    words = text.lower().split()
    # Keep words only if they aren't in the stop list and are alphanumeric
    return {w.strip(".,!?;:") for w in words if w not in STOP_WORDS and len(w) > 1}

def get_average_embedding(embeddings):
    if not embeddings:
        return []
    num_vectors = len(embeddings)
    return [sum(col) / num_vectors for col in zip(*embeddings)]

def get_subject_of_sentence(sentence):
    doc = nlp(sentence)
    subjects = []
    for token in doc:
        if "subj" in token.dep_:
            # Get every word in the subject's sub-tree and join them
            full_subject = "".join([t.text_with_ws for t in token.subtree])
            subjects.append(full_subject.strip())
    return subjects

def get_combined_embedding(paragraph, current_block_indices):
    return get_embedding(" ".join(paragraph[i] for i in sorted(current_block_indices)))
import spacy

def get_sentences_from_para(paragraph):
    doc = nlp(paragraph)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]