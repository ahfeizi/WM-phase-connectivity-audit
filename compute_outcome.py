#!/usr/bin/env python3
"""
Compute the primary outcome of the phase-connectivity reporting audit.

Reads coding_sheet.csv once it has been coded and reports:

  - the primary outcome, with a 95% Wilson interval
  - the same proportion by year, for the temporal-trend question
  - the source-space subset, reported separately
  - what has not been coded yet, so a partial run is still informative

Run it on a partly coded sheet as often as you like. It never writes to the
sheet.

    python compute_outcome.py coding_sheet.csv
    python compute_outcome.py coding_sheet.csv --no-ppc-rule

--no-ppc-rule turns off the PPC rule (see PPC_TOKEN below), so the outcome
can be reported both ways.
"""

import csv
import math
import sys
from collections import Counter, defaultdict

csv.field_size_limit(10 ** 7)

ZERO_LAG = ["plv", "coh", "phase_coh"]
ROBUST = ["pli", "wpli", "dwpli", "imcoh", "cipli"]

# PPC rule (D20). PPC, the pairwise phase consistency, is an unbiased estimator
# of squared PLV (Vinck et al., 2010), so it is as sensitive to zero-lag
# coupling as PLV. It has no flag column. With the rule on, a record whose
# other_measure contains "PPC" counts as having a zero-lag-sensitive measure.
# It is on by default; --no-ppc-rule turns it off.
PPC_TOKEN = "PPC"
NO_PPC_SWITCH = "--no-ppc-rule"


def flag(row, col):
    return (row.get(col) or "").strip() in ("1", "y", "yes", "x", "true")


def has_zero_lag(r, ppc_rule=True):
    return any(flag(r, c) for c in ZERO_LAG) or \
           (ppc_rule and PPC_TOKEN in (r.get("other_measure") or ""))


def zero_lag_only(r, ppc_rule=True):
    return has_zero_lag(r, ppc_rule) and not any(flag(r, c) for c in ROBUST)


def parse_args(argv, default_path):
    """Return (sheet path, ppc_rule) from the command line."""
    ppc_rule = NO_PPC_SWITCH not in argv
    rest = [a for a in argv if a != NO_PPC_SWITCH]
    return (rest[0] if rest else default_path), ppc_rule


def wilson(k, n, z=1.959963985):
    """Wilson score interval. Behaves at k=0 and k=n, unlike the normal approx."""
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centre - half), min(1.0, centre + half)


def main():
    path, ppc_rule = parse_args(sys.argv[1:], "coding_sheet.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))

    coded, uncoded, no_text = [], [], []
    for r in rows:
        note = (r.get("coder_note") or "").lower()
        has_measure = any(flag(r, c) for c in ZERO_LAG + ROBUST) or \
                      (r.get("other_measure") or "").strip()
        if "no-full-text" in note:
            no_text.append(r)
        elif has_measure and (r.get("space") or "").strip():
            coded.append(r)
        else:
            uncoded.append(r)

    print("=" * 66)
    print(f"AUDIT PRIMARY OUTCOME   {path}")
    print(f"PPC rule:               {'on' if ppc_rule else 'off'}")
    print("=" * 66)
    print(f"Records in sheet:       {len(rows)}")
    print(f"Coded:                  {len(coded)}")
    print(f"Not yet coded:          {len(uncoded)}")
    print(f"Full text unobtainable: {len(no_text)}")

    if not coded:
        print("\nNothing coded yet.")
        return

    # --- primary outcome -------------------------------------------------
    denom = [r for r in coded if (r.get("space") or "").strip() in ("sensor", "both")]
    src_only = [r for r in coded if (r.get("space") or "").strip() == "source"]

    def zl_only(r):
        return zero_lag_only(r, ppc_rule)

    k = sum(1 for r in denom if zl_only(r))
    n = len(denom)
    p, lo, hi = wilson(k, n)

    print("\n" + "-" * 66)
    print("PRIMARY OUTCOME  (sensor-space or both)")
    print("-" * 66)
    print(f"  zero-lag-sensitive measures only:  {k}/{n}")
    print(f"  proportion:                        {p:.3f}")
    print(f"  95% Wilson CI:                     [{lo:.3f}, {hi:.3f}]")

    gate = "MET" if p >= 0.60 else "NOT MET"
    print(f"\n  gate criterion 2 (>= 0.60):        {gate}")

    # --- by year ---------------------------------------------------------
    print("\n" + "-" * 66)
    print("BY YEAR")
    print("-" * 66)
    by_year = defaultdict(lambda: [0, 0])
    for r in denom:
        y = (r.get("year") or "?").strip()
        by_year[y][1] += 1
        if zl_only(r):
            by_year[y][0] += 1
    for y in sorted(by_year):
        kk, nn = by_year[y]
        bar = "#" * round(20 * kk / nn) if nn else ""
        print(f"  {y}  {kk:>3}/{nn:<3}  {kk/nn:.2f}  {bar}")

    # --- measure frequencies --------------------------------------------
    print("\n" + "-" * 66)
    print("MEASURE FREQUENCIES  (all coded records)")
    print("-" * 66)
    for c in ZERO_LAG + ROBUST:
        tag = "zero-lag" if c in ZERO_LAG else "robust"
        cnt = sum(1 for r in coded if flag(r, c))
        print(f"  {c:<10} {cnt:>4}   {tag}")

    other = Counter((r.get("other_measure") or "").strip()
                    for r in coded if (r.get("other_measure") or "").strip())
    if other:
        print("\n  other_measure:")
        for name, cnt in other.most_common():
            print(f"    {cnt:>3}  {name[:50]}")

    # --- source space ----------------------------------------------------
    if src_only:
        ks = sum(1 for r in src_only if zl_only(r))
        ps, los, his = wilson(ks, len(src_only))
        print("\n" + "-" * 66)
        print("SOURCE SPACE ONLY  (reported separately)")
        print("-" * 66)
        print(f"  zero-lag only: {ks}/{len(src_only)} = {ps:.3f} "
              f"[{los:.3f}, {his:.3f}]")

    # --- optional citation column ---------------------------------------
    checked = [r for r in coded if (r.get("cites_robust") or "").strip()
               and (r.get("cites_robust") or "").strip().lower() != "na"]
    if checked:
        cites_and_zero = sum(1 for r in checked
                             if flag(r, "cites_robust") and zl_only(r))
        pc, loc, hic = wilson(cites_and_zero, len(checked))
        print("\n" + "-" * 66)
        print("CITATION VS PRACTICE  (checked subset only)")
        print("-" * 66)
        print(f"  checked for Nolte / Stam / Vinck:  {len(checked)}")
        print(f"  cite one and report zero-lag only: {cites_and_zero}"
              f" = {pc:.3f} [{loc:.3f}, {hic:.3f}]")
        print(f"  gate criterion 4a (>= 0.20):       "
              f"{'MET' if pc >= 0.20 else 'NOT MET'}")

    # --- flags needing attention -----------------------------------------
    unsure = [r["rec_id"] for r in coded
              if "unsure" in (r.get("coder_note") or "").lower()]
    if unsure:
        print(f"\nMarked UNSURE ({len(unsure)}): {', '.join(unsure)}")

    none_named = [r["rec_id"] for r in coded
                  if not any(flag(r, c) for c in ZERO_LAG + ROBUST)]
    if none_named:
        print(f"\nOnly other_measure, no named index ({len(none_named)}): "
              f"{', '.join(none_named)}")
        print("  Check these: a paper with no within-frequency phase measure")
        print("  may belong outside the denominator.")


if __name__ == "__main__":
    main()
