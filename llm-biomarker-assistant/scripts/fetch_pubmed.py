from __future__ import annotations
import argparse
import json
import os
from Bio import Entrez, Medline


def fetch_pubmed(query: str, output: str, retmax: int = 20) -> None:
    Entrez.email = os.environ.get("NCBI_EMAIL", "your_email@example.com")
    Entrez.api_key = os.environ.get("NCBI_API_KEY") or None
    search = Entrez.read(Entrez.esearch(db="pubmed", term=query, retmax=retmax))
    pmids = search["IdList"]
    if not pmids:
        print("No PubMed records found.")
        return
    handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline", retmode="text")
    records = list(Medline.parse(handle))
    with open(output, "w", encoding="utf-8") as out:
        for record in records:
            abstract = record.get("AB", "")
            if not abstract:
                continue
            pmid = record.get("PMID", "")
            item = {
                "document_id": f"PMID-{pmid}",
                "source_type": "publication",
                "title": record.get("TI", ""),
                "year": int(record.get("DP", "0000")[:4]) if record.get("DP", "")[:4].isdigit() else None,
                "disease": "",
                "interventions": [],
                "biomarkers": [],
                "evidence_level": "unreviewed_publication",
                "study_design": "PubMed abstract; manually curate study design",
                "text": abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "is_synthetic": False,
            }
            out.write(json.dumps(item) + "\n")
    print(f"Saved {len(records)} PubMed records to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default='(TIGIT) AND (NSCLC OR "non-small cell lung cancer")')
    parser.add_argument("--output", default="data/raw/pubmed_tigit_nsclc.jsonl")
    parser.add_argument("--retmax", type=int, default=20)
    args = parser.parse_args()
    fetch_pubmed(args.query, args.output, args.retmax)
