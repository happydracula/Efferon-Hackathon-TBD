from llm_invoker import call_llm
SECTION_SELECTION_PROMPT = """
You are selecting relevant sections from a clinical paper.

Your task:
Identify the headings/subheadings most likely to contain:
- methodology
- population selection criteria
- statistical analysis
- outcomes/results
- prognostic evidence
- ROC/AUC analysis
- regression analysis

Return ONLY valid JSON.

OUTPUT FORMAT:
{{
  "relevant_sections": [<section_paths>]
}}

HEADINGS:
{headings}
"""

def extract_paths(
    obj,
    parent_key=""
):

    paths = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_key = (
                f"{parent_key}.{key}"
                if parent_key
                else key
            )

            paths.append(new_key)

            paths.extend(
                extract_paths(
                    value,
                    new_key
                )
            )

    elif isinstance(obj, list):

        for idx, item in enumerate(obj):

            new_key = (
                f"{parent_key}[{idx}]"
            )

            paths.extend(
                extract_paths(
                    item,
                    new_key
                )
            )

    return paths

def get_nested_value(
    obj,
    path
):
    """
    Retrieve nested value using dot-separated path.
    Example:
        path = "methods.population_selection"
    """

    keys = path.split(".")

    current = obj

    for key in keys:

        # Handle list indices like foo[0]
        if "[" in key and "]" in key:

            field = key[:key.index("[")]

            idx = int(
                key[key.index("[")+1:key.index("]")]
            )

            current = current[field][idx]

        else:
            current = current[key]

    return current


def identify_relevant_sections(
    paper_json
):

    paths = extract_paths(
        paper_json
    )

    headings = "\n".join(paths)

    prompt = (
        SECTION_SELECTION_PROMPT
        .format(
            headings=headings
        )
    )

    response = call_llm(prompt)

    relevant_sections = response[
        "relevant_sections"
    ]

    extracted_sections = {}

    for section in relevant_sections:

        path = section

        try:

            extracted_sections[path] = get_nested_value(
                    paper_json,
                    path
                )

        except Exception as e:

            extracted_sections[path] = {
                "category": section.get(
                    "category"
                ),

                "error": str(e)
            }
    return extracted_sections