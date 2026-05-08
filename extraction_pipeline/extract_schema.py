"""
extract_schema.py
-----------------
Step 3 of the extraction pipeline.

For each finding produced by extract_findings.py, calls the LLM with the
relevant paper sections to populate the full evidence schema.

No changes to prompt or logic vs. the original.  The only structural change is
that `extracted_evidence` is now scoped per-finding (it was accidentally shared
across the loop in the original, causing duplicate entries).
"""

from fetch_relevant_sections import identify_relevant_sections
from llm_invoker import call_llm
import json

DETAILED_EXTRACTION_PROMPT = """\
You are extracting structured prognostic evidence from a clinical research paper.

You are given:
1. A core analytical finding extracted from the abstract
2. Relevant methodology/results sections

Your task:
Extract detailed evidence related ONLY to this finding.

IMPORTANT:
- Use exact numerical values when available
- Preserve exact predictor wording
- Do not hallucinate missing values
- If unavailable, return null

Return ONLY valid JSON.

OUTPUT FORMAT:
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

FINDING:
{finding_json}

SECTIONS:
{sections_text}
"""


def extract_schema(findings: dict, paper_json: dict) -> list[dict]:
    """
    Parameters
    ----------
    findings   : output of extract_core_findings  — {"findings": [...]}
    paper_json : the full paper document dict

    Returns
    -------
    list of {"finding": …, "evidence": […]} objects  (matches sample output)
    """
    chunks = identify_relevant_sections(paper_json)
    sections_text = "\n\n".join(
        f"PATH: {path}\nTEXT:\n{text}" for path, text in chunks.items()
    )

    api_response = []
    for finding in findings.get("findings", []):
        prompt = DETAILED_EXTRACTION_PROMPT.format(
            finding_json=json.dumps(finding, indent=2),
            sections_text=sections_text,
        )
        response = call_llm(prompt)

        # Normalise: LLM sometimes returns a list, sometimes a single dict
        if isinstance(response, dict):
            evidence_list = [response]
        elif isinstance(response, list):
            evidence_list = response
        else:
            evidence_list = []

        api_response.append({
            "finding": finding,
            "evidence": evidence_list,
        })

    return api_response
