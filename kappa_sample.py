#!/usr/bin/env python3
"""
Blind accuracy assessment of the pre-screening pass.

The duplicate-pair agreement measured consistency: the same abstract labelled
twice, identically. It says nothing about accuracy. A systematic
misunderstanding of a rule reproduces itself with perfect consistency.

This script measures accuracy against the author's own judgement, on a random
sample coded without sight of the model's labels.

Two steps.

    python kappa_sample.py draw
        Draws 50 random records, writes kappa_sample.csv with ai_label and
        ai_reason stripped and an empty my_label column. Also writes a hidden
        answer key that you must not open.

    python kappa_sample.py score
        After you have filled my_label, compares against the key and reports
        Cohen's kappa, the confusion matrix, and every disagreement.

Do not open kappa_key.csv before scoring. Opening it invalidates the estimate.
"""

import csv
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(10**7)

OUTDIR = Path("stage0_output")
SOURCE = OUTDIR / "screening_sheet_final.csv"
SAMPLE = OUTDIR / "kappa_sample.csv"
KEY = OUTDIR / "kappa_key.csv"

N = 50
SEED = 20261002  # fixed so the draw is reproducible and auditable

LABELS = ["1", "0", "?"]


def draw():
    if not SOURCE.exists():
        sys.exit(f"Not found: {SOURCE}\nRun fix_dois.py first.")
    if SAMPLE.exists():
        sys.exit(
            f"{SAMPLE} already exists. Delete it deliberately if you want "
            f"to redraw - a redraw after seeing any label is not blind."
        )

    rows = list(csv.DictReader(SOURCE.open(encoding="utf-8-sig")))
    print(f"Source records: {len(rows)}")

    rng = random.Random(SEED)
    sample = rng.sample(rows, min(N, len(rows)))
    sample.sort(key=lambda r: r["rec_id"])

    # Blind sheet: everything needed to judge, nothing that reveals the answer.
    fields = ["rec_id", "year", "journal", "title", "abstract", "my_label", "my_reason"]
    with SAMPLE.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in sample:
            w.writerow(
                {**{k: r.get(k, "") for k in fields}, "my_label": "", "my_reason": ""}
            )

    with KEY.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(
            f, fieldnames=["rec_id", "ai_label", "ai_reason"], extrasaction="ignore"
        )
        w.writeheader()
        for r in sample:
            w.writerow(
                {
                    "rec_id": r["rec_id"],
                    "ai_label": r.get("ai_label", ""),
                    "ai_reason": r.get("ai_reason", ""),
                }
            )

    print(f"\nBlind sheet: {SAMPLE}")
    print(f"Answer key:  {KEY}   <- DO NOT OPEN")
    print(f"\nFill my_label with 1, 0 or ? for all {len(sample)} rows.")
    print("Use my_reason for anything you want to remember. Then:")
    print("    python kappa_sample.py score")


def kappa(a, b, labels):
    """Cohen's kappa for two label vectors."""
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    if pe == 1.0:
        return 1.0, po, pe
    return (po - pe) / (1 - pe), po, pe


def score():
    if not SAMPLE.exists() or not KEY.exists():
        sys.exit("Run 'draw' first.")

    mine = {r["rec_id"]: r for r in csv.DictReader(SAMPLE.open(encoding="utf-8-sig"))}
    key = {r["rec_id"]: r for r in csv.DictReader(KEY.open(encoding="utf-8-sig"))}

    blank = [k for k, r in mine.items() if not (r.get("my_label") or "").strip()]
    if blank:
        sys.exit(
            f"{len(blank)} rows still have an empty my_label "
            f"(first: {blank[0]}). Finish coding before scoring."
        )

    ids = sorted(set(mine) & set(key))
    human = [(mine[i]["my_label"] or "").strip() for i in ids]
    model = [(key[i]["ai_label"] or "").strip() for i in ids]

    bad = {l for l in human + model if l not in LABELS}
    if bad:
        sys.exit(f"Unexpected label values: {bad}. Use only 1, 0 or ?")

    k, po, pe = kappa(human, model, LABELS)

    print("=" * 64)
    print(f"BLIND ACCURACY ASSESSMENT   n = {len(ids)}")
    print("=" * 64)
    print(f"\nObserved agreement   {po:.3f}   ({int(po * len(ids))}/{len(ids)})")
    print(f"Chance agreement     {pe:.3f}")
    print(f"Cohen's kappa        {k:.3f}")

    print("\nConfusion matrix (rows = yours, columns = model):")
    m = defaultdict(int)
    for h, a in zip(human, model):
        m[(h, a)] += 1
    print("        " + "".join(f"{l:>7}" for l in LABELS))
    for h in LABELS:
        print(f"  {h:>5} " + "".join(f"{m[(h, a)]:>7}" for a in LABELS))

    dis = [
        (i, mine[i]["my_label"].strip(), key[i]["ai_label"].strip())
        for i in ids
        if mine[i]["my_label"].strip() != key[i]["ai_label"].strip()
    ]

    if dis:
        print(f"\nDisagreements ({len(dis)}):")
        for i, h, a in dis:
            print(f"\n  {i}   you={h}  model={a}")
            print(f"    {mine[i]['title'][:100]}")
            if mine[i].get("my_reason"):
                print(f"    yours: {mine[i]['my_reason'][:90]}")
            print(f"    model: {key[i]['ai_reason'][:90]}")

    print("\n" + "=" * 64)
    if k >= 0.80:
        print("kappa >= 0.80 - substantial. Review the remaining records as a")
        print("verification pass: scan, confirm, slow down only where something")
        print("looks wrong. Report this kappa in the methods.")
    elif k >= 0.60:
        print("kappa 0.60-0.80 - moderate. Review every record properly, and")
        print("go slowly in the high-risk reason categories. Report the kappa")
        print("and be explicit about it in the limitations.")
    else:
        print("kappa < 0.60 - the pre-screening labels are not reliable enough")
        print("to verify. Discard them and screen from scratch. Finding this")
        print("out now costs half an hour; finding it out at review costs the")
        print("paper.")
    print("=" * 64)
    print("\nThe disagreements above show where the manual was ambiguous.")
    print("Resolve each one, note the decision in deviations.md, and carry")
    print("the resolution into the full review.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "draw":
        draw()
    elif cmd == "score":
        score()
    else:
        sys.exit("Usage: python kappa_sample.py draw | score")
