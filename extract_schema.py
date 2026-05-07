from fetch_relevant_sections import identify_relevant_sections
from llm_invoker import call_llm
import json
DETAILED_EXTRACTION_PROMPT = """
You are extracting structured prognostic evidence
from a clinical research paper.

You are given:
1. A Core finding extracted from the abstract
2. Relevant methodology/results sections

Your task:
For the finding, extract:
- sample size
- outcome
- timing
- method
- effect size
1. A Core finding extracted from the abstract
2. Relevant methodology/results sections

Your task:
For the finding, extract:
- sample size
- outcome
- timing
- method
- effect size
- performance metrics
- notes

IMPORTANT:
- Preserve finding separation
- Shared study information may apply to multiple findings
- Use exact numerical values when available
- If a field is not available, return null

Return ONLY valid JSON.

OUTPUT FORMAT:
{{
  "evidence": [
    {{
      "population_type": "",
      "predictors": [],
      "affected_or_not": true,

      "sample_size": "",
      "outcome": "",
      "timing": "",
      "method": "",
      "effect_size": "",
      "performance": "",
      "notes": ""
    }}
  ]
}}

CORE FINDINGS:
{findings_json}

SECTIONS:
{sections_text}
"""

def extract_schema(
    findings,
    paper_json
):

    chunks = identify_relevant_sections(
        paper_json
    )

    sections_text = "\n\n".join([

    f"PATH: {path}\n"
    f"TEXT:\n{text}"

    for path, text in chunks.items()
])

    prompt = (
        DETAILED_EXTRACTION_PROMPT
        .format(
            findings_json=json.dumps(
                findings,
                indent=2
            ),
            sections_text=sections_text
        )
    )

    response = call_llm(prompt)

    return response