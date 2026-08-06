from __future__ import annotations
import argparse
import json
import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_trials(query: str, output: str, page_size: int = 25) -> None:
    response = requests.get(BASE_URL, params={"query.term": query, "pageSize": page_size, "format": "json"}, timeout=60)
    response.raise_for_status()
    studies = response.json().get("studies", [])
    with open(output, "w", encoding="utf-8") as out:
        for study in studies:
            protocol = study.get("protocolSection", {})
            ident = protocol.get("identificationModule", {})
            desc = protocol.get("descriptionModule", {})
            design = protocol.get("designModule", {})
            arms = protocol.get("armsInterventionsModule", {})
            nct_id = ident.get("nctId", "UNKNOWN")
            interventions = [x.get("name", "") for x in arms.get("interventions", [])]
            text = " ".join(filter(None, [desc.get("briefSummary", ""), desc.get("detailedDescription", "")]))
            item = {
                "document_id": nct_id,
                "source_type": "clinical_trial",
                "title": ident.get("briefTitle", ""),
                "year": None,
                "disease": "|".join(protocol.get("conditionsModule", {}).get("conditions", [])),
                "interventions": interventions,
                "biomarkers": [],
                "evidence_level": "registered_trial",
                "study_design": json.dumps(design, ensure_ascii=False),
                "text": text or ident.get("officialTitle", ""),
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
                "is_synthetic": False,
            }
            out.write(json.dumps(item) + "\n")
    print(f"Saved {len(studies)} trial records to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="TIGIT AND NSCLC")
    parser.add_argument("--output", default="data/raw/clinicaltrials_tigit_nsclc.jsonl")
    parser.add_argument("--page-size", type=int, default=25)
    args = parser.parse_args()
    fetch_trials(args.query, args.output, args.page_size)
