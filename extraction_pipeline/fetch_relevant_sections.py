"""
fetch_relevant_sections.py
--------------------------
Step 2 of the extraction pipeline.

Walks the paper JSON and returns the text sections most relevant to the
analytical findings.  In the original codebase this file contained a copy of
the CORE_FINDINGS_PROMPT (a paste error); that duplicate has been removed and
replaced with the actual section-identification logic.

The function `identify_relevant_sections` returns a dict of
  { "json_path": "section text", … }
which is then passed verbatim to extract_schema.py.
"""

RELEVANT_KEYS = {
    "abstract",
    "Materials And Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "Conclusions",
    "Statistical Analysis",
    "Methods",
    "Outcome",
    "Outcomes",
    "Patients",
    "Population",
}


def _flatten(obj, path: str = "") -> dict[str, str]:
    """
    Recursively walk a nested dict/list and collect every leaf string value,
    returning a flat {path: text} mapping.
    """
    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else key
            result.update(_flatten(value, child_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            result.update(_flatten(item, f"{path}[{i}]"))
    elif isinstance(obj, str) and obj.strip():
        result[path] = obj.strip()
    return result


def identify_relevant_sections(paper_json: dict) -> dict[str, str]:
    """
    Return the sections of *paper_json* that are most useful for evidence
    extraction.

    Strategy
    --------
    1. Collect all leaf strings with their JSON paths.
    2. Keep any path whose last segment matches a known relevant section name
       (case-insensitive).
    3. If nothing matches, fall back to returning everything (small papers).
    """
    all_sections = _flatten(paper_json)

    relevant = {}
    for path, text in all_sections.items():
        last_segment = path.split(".")[-1].strip("[]0123456789")
        if any(last_segment.lower() == rk.lower() for rk in RELEVANT_KEYS):
            relevant[path] = text

    # Fallback: return everything if heuristic matched nothing
    return relevant if relevant else all_sections
