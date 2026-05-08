"""
app.py
------
Entry point for the extraction pipeline.

Usage
-----
    python app.py                          # runs against the hard-coded JSON
    python app.py --paper path/to/paper.json   # runs against a JSON file
    python app.py --ingest                 # extract + store in PostgreSQL

The PDF → JSON parser is a future addition; for now supply the paper as a
Python dict (JSON variable below) or a .json file.
"""

import json
import argparse
from extract_findings import extract_core_findings
from extract_schema import extract_schema
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ---------------------------------------------------------------------------
# Sample paper JSON (replace / extend as needed)
# ---------------------------------------------------------------------------
JSON = {
    "abstract": {
        "Objective": (
            "To assess and compare the diagnostic accuracy of the Pediatric Risk of "
            "Mortality (PRISM) III score and Pediatric Sequential Organ Failure "
            "Assessment (p-SOFA) for the prediction of mortality in critically ill "
            "children."
        ),
        "Methodology": (
            "This was a cross-validation study conducted at the Pediatric Intensive Care "
            "Unit (PICU) of the National Institute of Child Health Karachi from February "
            "2021 to July 2021. Two hundred eighty-six critically ill children of age one "
            "month to 15 years of either gender staying in PICU for more than 24 hours "
            "were included. Within 24 hours of admission, the p-SOFA and PRISM III 24 "
            "scores were calculated for all eligible children. The outcome of the study "
            "was mortality within 30 days of PICU admitted children. Data were analyzed "
            "using Statistical Package for the Social Sciences (SPSS) version 23."
        ),
        "Results": (
            "The median age was 24 months (range: 1-144 months). The 30-day mortality "
            "was estimated as 57%. The p-SOFA and PRISM scores were significantly greater "
            "in children who did not survive than survivors. The maximum p-SOFA score "
            "(area under the curve (AUC)=0.81, 95% CI=0.76-0.86, p=0.001) and PRISM III "
            "24 score (AUC=0.75, 95% CI=0.69-0.81, p=0.001) had good discrimination for "
            "30-day mortality. For the prediction of 30-day mortality at the cut-off value "
            "of p-SOFA>2, the sensitivity was 93.87%, specificity was 38.21%, and accuracy "
            "was 69.93%. Whereas at the cut-off value of PRISM III 24 score>8, the "
            "sensitivity was 55.83%, specificity was 77.24%, and accuracy was 65.03%."
        ),
    },
    "Materials And Methods": (
        "From February to July 2021, cross-validation research was done in the PICU of "
        "the National Institute of Child Health (NICH) in Karachi. A nonprobability "
        "consecutive sampling approach was used to include critically ill children aged "
        "one month to 15 years. Within 24 hours of admission, the p-SOFA score was "
        "calculated. p-SOFA score of higher than 2 is considered as a predictor of "
        "mortality. PRISM III score was calculated within 24 hours after admission. A "
        "score of higher than 8 on the PRISM III 24 was deemed a predictor of mortality. "
        "Mortality within 30 days was the outcome of the study."
    ),
    "Results": (
        "We included 286 children in the study. The median age was 24 months "
        "(range: 1-144 months). The 30-day mortality was estimated as 57%."
    ),
}


def run_extraction(paper_json: dict) -> list[dict]:
    core_findings = extract_core_findings(paper_json)
    result = extract_schema(core_findings, paper_json)
    return result


def main():
    parser = argparse.ArgumentParser(description="Sepsis Atlas extraction pipeline")
    parser.add_argument("--paper", help="Path to a paper JSON file", default=None)
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="After extraction, store results in PostgreSQL/pgvector",
    )
    args = parser.parse_args()

    if args.paper:
        with open(args.paper) as f:
            paper_json = json.load(f)
    else:
        paper_json = JSON

    result = run_extraction(paper_json)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.ingest:
        # Import here so the module is optional when just running extraction
        from db.ingest import ingest_extraction_result
        paper_id = paper_json.get("paper_id", "unknown")
        ingest_extraction_result(paper_id, paper_json, result)
        print(f"\n[app] Ingested {len(result)} finding(s) into PostgreSQL.")


if __name__ == "__main__":
    main()
