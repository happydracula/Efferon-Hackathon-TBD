"""
batch_ingest.py
---------------
Ingest a directory of paper JSON files into the Sepsis Atlas.

Usage
-----
    python batch_ingest.py --dir papers/          # each .json file = one paper
    python batch_ingest.py --file paper.json      # single file
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "extraction_pipeline"))

from extraction_pipeline.app import run_extraction
from db.ingest import ingest_extraction_result
from db.connection import apply_schema


def ingest_file(path: str) -> None:
    with open(path) as f:
        paper_json = json.load(f)

    paper_id = paper_json.get("paper_id") or os.path.splitext(os.path.basename(path))[0]
    title = paper_json.get("title")

    print(f"\n[batch] Processing '{paper_id}' …")
    result = run_extraction(paper_json)
    ingest_extraction_result(paper_id, paper_json, result, title=title)
    ev_count = sum(len(i.get("evidence", [])) for i in result)
    print(f"[batch] ✓ {len(result)} finding(s), {ev_count} evidence row(s) stored.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir",  help="Directory of .json paper files")
    parser.add_argument("--file", help="Single .json paper file")
    args = parser.parse_args()

    apply_schema()

    if args.file:
        ingest_file(args.file)
    elif args.dir:
        files = [
            os.path.join(args.dir, f)
            for f in os.listdir(args.dir)
            if f.endswith(".json")
        ]
        print(f"[batch] Found {len(files)} JSON file(s) in '{args.dir}'")
        for path in sorted(files):
            try:
                ingest_file(path)
            except Exception as exc:
                print(f"[batch] ✗ Failed {path}: {exc}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
