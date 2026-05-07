from fetch_relevant_sections import (
    identify_relevant_sections
)

from llm_invoker import call_llm

import json


DETAILED_EXTRACTION_PROMPT = """
You are extracting structured prognostic evidence
from a clinical research paper.

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

    extracted_evidence = []
    api_response = []

    for finding in findings["findings"]:

        prompt = (
            DETAILED_EXTRACTION_PROMPT
            .format(
                finding_json=json.dumps(
                    finding,
                    indent=2
                ),

                sections_text=sections_text
            )
        )

        response = call_llm(prompt)

        # Parse if response is string
        if isinstance(response, str):

            response = response.strip()

            if response.startswith("```json"):
                response = response.removeprefix(
                    "```json"
                )

            if response.endswith("```"):
                response = response.removesuffix(
                    "```"
                )

            response = response.strip()

            response = json.loads(response)

        extracted_evidence.append(
            response
        )
        api_response.append({
            "finding":finding,
            "evidence":extracted_evidence
        })

    return api_response