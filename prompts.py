RESEARCH_EXTRACTION_PROMPT = """
ACT AS: A Senior Clinical Data Abstractor specializing in Critical Care and Sepsis research.

TASK:
Analyze the provided 'SOURCE MATERIAL' which contains evidence blocks from a medical study. 
Extract data into a structured JSON format following the SCHEMA provided.

CONSTRAINTS:
1. ONLY use information present in the source. Use "N/A" if info is missing.
2. If multiple values exist (e.g., multiple Performance metrics), list them all in the string.
3. Be specific: For 'Timing', look for things like 'at admission', 'within 24h', etc.
4. For 'Effect Size', include 95% Confidence Intervals (CI) and p-values if available.
5. Be as short and specific as possible, restrict values to a few words unless absolutely necessary.
6. Focus ONLY on the predictor specified in 'predictor_terms', ignore all others.

JSON SCHEMA DEFINITIONS:
- Study: Short name (e.g., Baloch et al. 2022).
- Population: Patient characteristics (e.g., Septic shock, ICU patients).
- Sample Size: Total (N) and any group breakdowns.
- Predictor: The primary variable being studied (e.g., Lactate, PCT, SOFA).
- Outcome: What is being predicted (e.g., 28-day mortality).
- Timing: When measurements were taken.
- Method: Statistical approach (e.g., Logistic Regression, AUROC).
- Effect Size: Hazard Ratios, Odds Ratios, or Beta coefficients.
- Performance: Sensitivity, Specificity, or AUROC values.
- Notes: Any key limitations or unique findings.
- Source: The specific section of the paper this was found in.

OUTPUT FORMAT:
Return ONLY a valid JSON object with the following keys:
["Study", "Population", "Sample Size", "Predictor", "Outcome", "Timing", "Method", "Effect Size", "Performance", "Notes", "Source"]
"""


CORE_FINDINGS_PROMPT = """
You are analyzing the abstract of a clinical research paper about sepsis.

Your task is to identify ONLY biomarkers, laboratory markers,
clinical scores, or physiological indicators that were explicitly
associated with:

- sepsis mortality
- non-survival
- death
- fatal outcome
- reduced survival
- poor survival prognosis

Return ONLY biomarkers that demonstrated an association
with survival outcomes in sepsis patients.

Exclude biomarkers that were:
- diagnostic only
- unrelated to mortality
- merely measured
- mentioned without prognostic significance

For each biomarker:
- return a canonical medical name
- extract abbreviations and synonymous forms
- include lexical variants if obvious from the text

Return ONLY valid JSON.

OUTPUT FORMAT:
{{
  "biomarkers": [
    {{
      "canonical_name": "Interleukin-6",
      "synonyms": [
        "IL-6",
        "interleukin 6"
      ]
    }},
    {{
      "canonical_name": "Lactate",
      "synonyms": [
        "serum lactate",
        "blood lactate",
        "lactic acid"
      ]
    }}
  ]
}}

IMPORTANT:
- Return ONLY biomarkers associated with non-survival
- Do NOT include explanations
- Do NOT include outcomes
- Do NOT include statistics
- Do NOT include duplicate biomarkers
- Normalize biomarker names where possible

ABSTRACT:
{abstract_text}
"""
