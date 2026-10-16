#!/usr/bin/env python3
"""
Stage 0 of the phase-connectivity reporting audit - with abstracts.

Retrieves candidate records from PubMed and Europe PMC, including abstracts,
deduplicates, and writes a screening sheet.

The output CSV has four empty columns:
    ai_label, ai_reason       - filled by the LLM pre-screening pass
    include, exclusion_reason - filled by the human screener (authoritative)

Requires: requests
    python -m pip install requests

Usage:
    python stage0_search.py            # counts only
    python stage0_search.py --fetch    # download records + abstracts to CSV
"""

import argparse
import csv
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

EMAIL = "your.name@example.org"  # your contact e-mail for NCBI E-utilities
TOOL = "phase-connectivity-audit"

YEAR_MIN = 2015
YEAR_MAX = 2025

OUTDIR = Path("stage0_output")

# ----------------------------------------------------------------------------
# Query concepts  (v1.1 - see deviations.md)
# ----------------------------------------------------------------------------

MODALITY = [
    "EEG[tiab]",
    "electroencephalogra*[tiab]",
]

TASK = [
    '"working memory"[tiab]',
    '"n-back"[tiab]',
    '"n back"[tiab]',
    "Sternberg[tiab]",
    '"delayed match"[tiab]',
    '"delayed matching"[tiab]',
    '"delayed match-to-sample"[tiab]',
    '"short-term memory"[tiab]',
    '"short term memory"[tiab]',
]

MEASURE = [
    "connectivity[tiab]",
    "synchron*[tiab]",
    "coupling[tiab]",
    "coherence[tiab]",
    '"phase locking"[tiab]',
    '"phase-locking"[tiab]',
    "PLV[tiab]",
    '"phase lag index"[tiab]',
    '"phase-lag index"[tiab]',
    "wPLI[tiab]",
    "dwPLI[tiab]",
    '"imaginary coherence"[tiab]',
    '"imaginary coherency"[tiab]',
]


def _block(terms):
    return "(" + " OR ".join(terms) + ")"


PUBMED_QUERY = " AND ".join([
    _block(MODALITY),
    _block(TASK),
    _block(MEASURE),
    f"({YEAR_MIN}:{YEAR_MAX}[dp])",
    "english[la]",
])


def _epmc_block(terms):
    cleaned = []
    for t in terms:
        t = re.sub(r"\[[a-z]+\]", "", t)
        t = t.replace("*", "")
        cleaned.append(f"ABSTRACT:{t}")
    return "(" + " OR ".join(cleaned) + ")"


EPMC_QUERY = " AND ".join([
    _epmc_block(MODALITY),
    _epmc_block(TASK),
    _epmc_block(MEASURE),
    f"(PUB_YEAR:[{YEAR_MIN} TO {YEAR_MAX}])",
    "(LANG:eng)",
    "(SRC:MED OR SRC:PMC)",
])

# ----------------------------------------------------------------------------
# PubMed
# ----------------------------------------------------------------------------

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def pubmed_count(query):
    r = requests.get(
        f"{EUTILS}/esearch.fcgi",
        params={"db": "pubmed", "term": query, "retmode": "json",
                "rettype": "count", "email": EMAIL, "tool": TOOL},
        timeout=60,
    )
    r.raise_for_status()
    return int(r.json()["esearchresult"]["count"])


def pubmed_pmids(query, retmax=10000):
    r = requests.get(
        f"{EUTILS}/esearch.fcgi",
        params={"db": "pubmed", "term": query, "retmode": "json",
                "retmax": retmax, "email": EMAIL, "tool": TOOL},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["esearchresult"].get("idlist", [])


def _text(node):
    """Flatten an element's text, including structured-abstract children."""
    if node is None:
        return ""
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def pubmed_records(pmids, batch=100):
    """efetch gives title, journal, year, DOI and abstract in one call."""
    out = []
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

        for art in root.findall(".//PubmedArticle"):
            pmid = _text(art.find(".//PMID"))
            title = _text(art.find(".//ArticleTitle"))

            # Structured abstracts: keep the section labels, they carry signal
            parts = []
            for ab in art.findall(".//Abstract/AbstractText"):
                label = ab.get("Label")
                body = _text(ab)
                parts.append(f"{label}: {body}" if label else body)
            abstract = " ".join(parts)

            doi = ""
            for aid in art.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = (aid.text or "").lower().strip()

            year = ""
            for path in (".//ArticleDate/Year", ".//PubDate/Year",
                         ".//PubDate/MedlineDate"):
                val = _text(art.find(path))
                if val:
                    year = val[:4]
                    break

            ptypes = [_text(p) for p in art.findall(".//PublicationType")]

            out.append({
                "source": "pubmed",
                "id": pmid,
                "doi": doi,
                "year": year,
                "journal": _text(art.find(".//Journal/Title")),
                "pubtypes": "; ".join(ptypes),
                "title": title,
                "abstract": abstract,
            })

        print(f"  pubmed {min(i + batch, len(pmids))}/{len(pmids)}", flush=True)
        time.sleep(0.4)
    return out


# ----------------------------------------------------------------------------
# Europe PMC
# ----------------------------------------------------------------------------

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def epmc_search(query, fetch=False, page_size=100):
    records, cursor, total = [], "*", None
    while True:
        r = requests.get(
            EPMC,
            params={"query": query, "format": "json",
                    "resultType": "core" if fetch else "idlist",
                    "pageSize": 1 if not fetch else page_size,
                    "cursorMark": cursor},
            timeout=180,
        )
        r.raise_for_status()
        data = r.json()
        if total is None:
            total = data.get("hitCount", 0)
        if not fetch:
            return total, []

        for rec in data.get("resultList", {}).get("result", []):
            records.append({
                "source": "epmc",
                "id": rec.get("id", ""),
                "doi": (rec.get("doi") or "").lower().strip(),
                "year": str(rec.get("pubYear", "")),
                "journal": rec.get("journalTitle", ""),
                "pubtypes": "; ".join(
                    rec.get("pubTypeList", {}).get("pubType", []) or []),
                "title": (rec.get("title") or "").strip(),
                "abstract": re.sub(r"\s+", " ",
                                   rec.get("abstractText") or "").strip(),
            })

        nxt = data.get("nextCursorMark")
        print(f"  epmc {len(records)}/{total}", flush=True)
        if not nxt or nxt == cursor or len(records) >= total:
            break
        cursor = nxt
        time.sleep(0.3)
    return total, records


# ----------------------------------------------------------------------------
# Deduplication
# ----------------------------------------------------------------------------

def norm_title(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def dedupe(records):
    by_doi, by_title, kept = set(), set(), []
    for rec in sorted(records, key=lambda r: 0 if r["source"] == "pubmed" else 1):
        doi, tkey = rec["doi"], norm_title(rec["title"])
        if doi and doi in by_doi:
            continue
        if not doi and tkey and tkey in by_title:
            continue
        if doi:
            by_doi.add(doi)
        if tkey:
            by_title.add(tkey)
        kept.append(rec)
    return kept


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

FIELDS = [
    "rec_id", "source", "id", "doi", "year", "journal", "pubtypes",
    "title", "abstract",
    "ai_label", "ai_reason",          # LLM pre-screening pass
    "include", "exclusion_reason",    # human screener - authoritative
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    args = ap.parse_args()

    OUTDIR.mkdir(exist_ok=True)

    print("=" * 72)
    print("STAGE 0 - candidate pool")
    print("=" * 72)

    print("\nConcept-level counts (sanity check):")
    for name, terms in [("modality", MODALITY), ("task", TASK), ("measure", MEASURE)]:
        q = f"{_block(terms)} AND ({YEAR_MIN}:{YEAR_MAX}[dp]) AND english[la]"
        print(f"  {name:10s} {pubmed_count(q):>9,}")
        time.sleep(0.4)

    print("\nCombined:")
    pm_total = pubmed_count(PUBMED_QUERY)
    print(f"  PubMed      {pm_total:>9,}")
    time.sleep(0.4)
    epmc_total, _ = epmc_search(EPMC_QUERY, fetch=False)
    print(f"  Europe PMC  {epmc_total:>9,}")

    (OUTDIR / "queries.json").write_text(json.dumps({
        "run_date": time.strftime("%Y-%m-%d"),
        "protocol_version": "1.1",
        "year_range": [YEAR_MIN, YEAR_MAX],
        "pubmed_query": PUBMED_QUERY, "pubmed_hits": pm_total,
        "epmc_query": EPMC_QUERY, "epmc_hits": epmc_total,
    }, indent=2), encoding="utf-8")

    if not args.fetch:
        print("\nRe-run with --fetch to download records and abstracts.")
        return

    print("\nFetching records and abstracts...")
    records = pubmed_records(pubmed_pmids(PUBMED_QUERY))
    _, epmc_recs = epmc_search(EPMC_QUERY, fetch=True)
    records.extend(epmc_recs)

    unique = dedupe(records)
    for n, rec in enumerate(unique, start=1):
        rec["rec_id"] = f"R{n:04d}"
        rec["ai_label"] = ""
        rec["ai_reason"] = ""
        rec["include"] = ""
        rec["exclusion_reason"] = ""

    no_abstract = sum(1 for r in unique if not r["abstract"])

    out = OUTDIR / "screening_sheet.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(unique)

    print("\n" + "=" * 72)
    print(f"Retrieved:        {len(records):,}")
    print(f"After dedupe:     {len(unique):,}")
    print(f"Without abstract: {no_abstract:,}  (screen on title + full text)")
    print(f"Written to:       {out}")
    print("=" * 72)


if __name__ == "__main__":
    main()
