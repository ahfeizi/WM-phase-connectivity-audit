#!/usr/bin/env python3
"""
Post-hoc deduplication of the labelled screening sheet.

Two jobs:

1. Diagnose why dedupe under-merged (missing DOIs vs title mismatches), so the
   failure can be described accurately in the methods rather than guessed at.

2. Merge duplicates, keeping the PubMed row, and write a clean sheet. The AI
   labels on the discarded twins are retained as a side product: duplicate pairs
   were labelled independently, so their agreement is a within-rater consistency
   estimate for the pre-screening pass, obtained for free.

Usage:
    python dedupe_check.py stage0_output/screening_sheet.csv
"""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

IN = Path(sys.argv[1] if len(sys.argv) > 1
          else "stage0_output/screening_sheet.csv")
OUT = IN.with_name("screening_sheet_dedup.csv")
REPORT = IN.with_name("dedupe_report.txt")


def norm_title(t):
    """Aggressive normalisation: strip markup, punctuation, case, whitespace."""
    t = re.sub(r"<[^>]+>", " ", t or "")          # HTML/XML tags
    t = re.sub(r"&[a-z]+;", " ", t)               # entities
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    rows = list(csv.DictReader(IN.open(encoding="utf-8-sig")))
    fields = list(rows[0].keys())
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    say("=" * 68)
    say(f"DEDUPE DIAGNOSIS - {IN.name}")
    say("=" * 68)
    say(f"Rows: {len(rows)}")

    by_source = Counter(r["source"] for r in rows)
    say(f"By source: {dict(by_source)}")

    # --- Why did dedupe under-merge? --------------------------------------
    missing_doi = Counter(r["source"] for r in rows if not r["doi"].strip())
    say(f"\nRows with no DOI: {sum(missing_doi.values())}  {dict(missing_doi)}")
    say("  (a DOI missing on one side forces the weaker title match)")

    # --- Group by DOI, then by normalised title ---------------------------
    groups = defaultdict(list)
    for r in rows:
        doi = r["doi"].strip().lower()
        key = ("doi", doi) if doi else ("title", norm_title(r["title"]))
        groups[key].append(r)

    # second pass: merge title groups into DOI groups where a title matches
    title_index = {}
    for key, members in groups.items():
        if key[0] == "doi":
            for m in members:
                tk = norm_title(m["title"])
                if tk:
                    title_index[tk] = key

    merged = defaultdict(list)
    for key, members in groups.items():
        if key[0] == "title" and key[1] in title_index:
            merged[title_index[key[1]]].extend(members)
        else:
            merged[key].extend(members)

    dup_groups = {k: v for k, v in merged.items() if len(v) > 1}
    n_dupes = sum(len(v) - 1 for v in dup_groups.values())

    say(f"\nDuplicate groups: {len(dup_groups)}")
    say(f"Redundant rows:   {n_dupes}")
    say(f"Unique records:   {len(merged)}")

    # --- Label agreement across duplicate pairs ---------------------------
    agree = disagree = 0
    disagreements = []
    for key, members in dup_groups.items():
        labels = {m["ai_label"].strip() for m in members}
        if len(labels) == 1:
            agree += 1
        else:
            disagree += 1
            disagreements.append((
                [m["rec_id"] for m in members],
                [m["ai_label"] for m in members],
                members[0]["title"][:70],
            ))

    if dup_groups:
        pct = 100 * agree / len(dup_groups)
        say(f"\nAI label agreement across duplicate pairs: "
            f"{agree}/{len(dup_groups)} ({pct:.1f}%)")
        if disagreements:
            say("\nDisagreements (resolve these by hand):")
            for ids, labs, title in disagreements:
                say(f"  {'/'.join(ids)}  labels={labs}  {title}")

    # --- Write the merged sheet -------------------------------------------
    kept = []
    for key, members in merged.items():
        members.sort(key=lambda r: 0 if r["source"] == "pubmed" else 1)
        keep = dict(members[0])
        if len(members) > 1:
            keep["duplicate_of"] = ";".join(m["rec_id"] for m in members[1:])
            keep["twin_labels"] = ";".join(m["ai_label"] for m in members[1:])
        else:
            keep["duplicate_of"] = ""
            keep["twin_labels"] = ""
        kept.append(keep)

    kept.sort(key=lambda r: r["rec_id"])

    out_fields = fields + ["duplicate_of", "twin_labels"]
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)

    # --- Label distribution on the clean sheet ----------------------------
    dist = Counter(r["ai_label"].strip() for r in kept)
    say("\n" + "=" * 68)
    say("AI LABELS ON THE DEDUPLICATED SHEET")
    say("=" * 68)
    for lab in ("1", "0", "?"):
        say(f"  {lab or '(blank)':>3}  {dist.get(lab, 0):>4}")
    other = {k: v for k, v in dist.items() if k not in ("1", "0", "?")}
    if other:
        say(f"  unexpected labels: {other}")

    reasons = Counter(r["ai_reason"].strip().lower()
                      for r in kept if r["ai_label"].strip() == "0")
    say("\nTop exclusion reasons (free text, indicative only):")
    for reason, n in reasons.most_common(12):
        say(f"  {n:>4}  {reason[:60]}")

    say(f"\nWritten: {OUT}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    say(f"Report:  {REPORT}")


if __name__ == "__main__":
    main()
