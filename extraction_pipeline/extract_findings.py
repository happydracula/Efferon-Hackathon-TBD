"""
extract_findings.py
-------------------
Step 1 of the extraction pipeline.

Given the abstract section of a paper (as a plain string), calls the LLM to
identify each distinct analytical *finding* — a (population, predictors,
affected_or_not) triple.

No changes were made to the prompt or logic relative to the original codebase.
The function signature was widened to accept either a plain string *or* the
full JSON document dict (in which case it extracts the abstract automatically).
"""

from llm_invoker import call_llm

CORE_FINDINGS_PROMPT = """\
You are analyzing the abstract of a clinical research paper.
Your task is to identify the key analytical findings described in the abstract.

A finding consists of:
- the population or subgroup being analyzed
- the predictors/biomarkers/scores evaluated
- whether the predictors were associated with, predictive of,
  or significantly related to an outcome

IMPORTANT:
- Different population groups MUST be separated
- Predictors discussed together may remain grouped together
- "affected_or_not" should be TRUE if:
  - predictors were associated with outcomes
  - predictors showed prognostic value
  - statistically significant findings were reported
  - predictive performance was reported
- "affected_or_not" should be FALSE if:
  - no association was found
  - findings were negative
  - predictors were not significant

Examples of population types:
- ICU patients with septic shock
- ED patients with suspected infection
- postoperative abdominal sepsis patients

Return ONLY valid JSON.

OUTPUT FORMAT:
{{
  "findings": [
    {{
      "population_type": "ED patients with suspected infection",
      "predictors": ["lymphocyte count", "lactate"],
      "affected_or_not": true
    }}
  ]
}}

INSTRUCTIONS:
- Return ALL distinct findings
- Separate findings by population/subgroup
- Use concise clinical wording
- Return empty list if no findings exist

ABSTRACT:
{abstract_text}
"""


def extract_core_findings(abstract_input) -> dict:
    """
    Parameters
    ----------
    abstract_input : str | dict
        Either a plain abstract string, or the full paper JSON dict.
        When a dict is given the abstract is assembled from the "abstract" key.

    Returns
    -------
    dict  – {"findings": [ {population_type, predictors, affected_or_not}, … ]}
    """
    if isinstance(abstract_input, dict):
        abstract = abstract_input.get("abstract", {})
        if isinstance(abstract, dict):
            abstract_text = "\n\n".join(
                f"{k}:\n{v}" for k, v in abstract.items()
            )
        else:
            abstract_text = str(abstract)
    else:
        abstract_text = abstract_input

    prompt = CORE_FINDINGS_PROMPT.format(abstract_text=abstract_text)
    return call_llm(prompt)
