from llm_invoker import call_llm

CORE_FINDINGS_PROMPT = """
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
      "population_type":
        "ED patients with suspected infection",

      "predictors": [
        "lymphocyte count",
        "lactate"
      ],

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


def extract_core_findings(
    abstract_text: str
):

    prompt = CORE_FINDINGS_PROMPT.format(
        abstract_text=abstract_text
    )

    response = call_llm(prompt)
    return response

