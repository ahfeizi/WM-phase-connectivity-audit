#!/usr/bin/env python3
"""
Repair the PubMed DOI field in the screened CSV.

Cause of the corruption: stage0_search.py used art.findall(".//ArticleId"),
which descends into <ReferenceList> and therefore matched the ArticleId of each
CITED REFERENCE, not of the article itself. The last match won, so every PubMed
row carries the DOI of the last reference in its bibliography.

Consequence: DOI-based deduplication never matched, leaving 133 unmerged
duplicate pairs, and the recorded DOIs cannot be used to retrieve full texts.

This script re-fetches the correct DOI for each PubMed row by PMID, merges the
remaining duplicates on normalised title, and writes a repaired sheet. The
ai_label and ai_reason columns are carried through unchanged.

Usage:
    python fix_dois.py stage0_output/screening_sheet_dedup.csv
"""

import csv
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import requests

csv.field_size_limit(10 ** 7)

EMAIL = "your.name@example.org"  # your contact e-mail for NCBI E-utilities
TOOL = "phase-connectivity-audit"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

IN = Path(sys.argv[1] if len(sys.argv) > 1
          else "stage0_output/screening_sheet_dedup.csv")
OUT = IN.with_name("screening_sheet_final.csv")
REPORT = IN.with_name("fix_dois_report.txt")


def norm_title(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = re.sub(r"&[a-z]+;", " ", t).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def correct_dois(pmids, batch=150):
    """Fetch the article's OWN DOI. Scoped to PubmedData/ArticleIdList, with
    ELocationID as fallback. Never descends into ReferenceList."""
    out = {}
    for i in range(0, len(pmids), batch):
        chunk = pmids[i:i + batch]
        r = requests.post(
            f"{EUTILS}/efetch.fcgi",
            data={"db": "pubmed", "id": ",".join(chunk), "retmode": "xml",
                  "email": EMAIL, "tool": TOOL},
            timeout=180,
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)

        for art in root.iter():
            if art.tag not in ("PubmedArticle", "PubmedBookArticle"):
                continue
            pmid_el = art.find("./MedlineCitation/PMID")
            if pmid_el is None:
                pmid_el = art.find("./BookDocument/PMID")
            if pmid_el is None:
                continue
            pmid = (pmid_el.text or "").strip()

            doi = ""
            for aid in art.findall("./PubmedData/ArticleIdList/ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = (aid.text or "").strip().lower()
                    break
            if not doi:
                for el in art.findall("./MedlineCitation/Article/ELocationID"):
                    if el.get("EIdType") == "doi":
                        doi = (el.text or "").strip().lower()
                        break
            out[pmid] = doi

        print(f"  {min(i + batch, len(pmids))}/{len(pmids)}", flush=True)
        time.sleep(0.4)
    return out


def main():
    rows = list(csv.DictReader(IN.open(encoding="utf-8-sig")))
    fields = list(rows[0].keys())
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    say("=" * 68)
    say(f"DOI REPAIR - {IN.name}")
    say("=" * 68)
    say(f"Rows in: {len(rows)}")

    pmids = [r["id"].strip() for r in rows
             if r["source"] == "pubmed" and r["id"].strip()]
    say(f"PubMed rows to re-fetch: {len(pmids)}")

    say("\nFetching correct DOIs...")
    fixed = correct_dois(pmids)

    changed = missing = 0
    for r in rows:
        if r["source"] != "pubmed":
            continue
        new = fixed.get(r["id"].strip(), "")
        if not new:
            missing += 1
            continue
        if new != r["doi"].strip().lower():
            changed += 1
        r["doi"] = new

    say(f"\nDOIs corrected:      {changed}")
    say(f"DOIs still missing:  {missing}")

    # --- merge duplicates on title, keeping the PubMed row -----------------
    seen, kept, dropped = {}, [], []
    for r in sorted(rows, key=lambda r: (0 if r["source"] == "pubmed" else 1,
                                         r["rec_id"])):
        k = norm_title(r["title"])
        if k and k in seen:
            dropped.append((r, seen[k]))
            continue
        if k:
            seen[k] = r
        kept.append(r)
    kept.sort(key=lambda r: r["rec_id"])

    say(f"\nUnique records:      {len(kept)}")
    say(f"Merged as duplicate: {len(dropped)}")

    # --- independent double labelling -------------------------------------
    if dropped:
        agree = sum(1 for a, b in dropped
                    if a["ai_label"].strip() == b["ai_label"].strip())
        say(f"\nIndependent double labelling of duplicate pairs:")
        say(f"  {agree}/{len(dropped)} agreement "
            f"({100 * agree / len(dropped):.1f}%)")
        say("  (each pair was labelled twice without the pass knowing they")
        say("   were the same paper - this is a within-rater consistency")
        say("   estimate for the pre-screening tool, report it as such)")
        for a, b in dropped:
            if a["ai_label"].strip() != b["ai_label"].strip():
                say(f"    MISMATCH {a['rec_id']}={a['ai_label']} "
                    f"vs {b['rec_id']}={b['ai_label']}  {a['title'][:60]}")

    # --- year sanity ------------------------------------------------------
    years = Counter(r["year"] for r in kept)
    out_of_range = {y: n for y, n in years.items()
                    if not y.isdigit() or not (2015 <= int(y) <= 2025)}
    if out_of_range:
        say(f"\nRecords outside the 2015-2025 window: {out_of_range}")
        say("  (PubDate vs ArticleDate disagreement - check before coding)")

    # --- final label distribution -----------------------------------------
    dist = Counter(r["ai_label"].strip() for r in kept)
    say("\n" + "=" * 68)
    say("CORRECTED ai_label DISTRIBUTION")
    say("=" * 68)
    for lab in ("1", "0", "?"):
        say(f"  {lab}  {dist.get(lab, 0):>4}")

    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)

    say(f"\nWritten: {OUT}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    say(f"Report:  {REPORT}")


if __name__ == "__main__":
    main()
