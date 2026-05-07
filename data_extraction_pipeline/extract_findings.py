from llm_invoker import call_llm
from prompts import CORE_FINDINGS_PROMPT

def extract_core_findings(abstract_text: str):

    prompt = CORE_FINDINGS_PROMPT.format(
        abstract_text=abstract_text
    )

    response = call_llm(prompt)
    return response