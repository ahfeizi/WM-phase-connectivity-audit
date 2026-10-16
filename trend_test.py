#!/usr/bin/env python3
"""
Cochran-Armitage test for trend over publication year in the primary outcome
of the phase-connectivity reporting audit.

Uses the primary denominator of compute_outcome.py (coded records, space =
sensor or both) and its zero-lag-only classification. Scores are publication
years; p is two-sided from the normal approximation. It never writes to the
sheet.

    python trend_test.py [coding_sheet.csv] [--no-ppc-rule]

The PPC rule is defined in compute_outcome.py and is on by default.

Default sheet: stage0_output/coding_sheet.csv next to this script.
"""

import csv
import math
import os
import sys
from collections import defaultdict

from compute_outcome import ZERO_LAG, ROBUST, flag, zero_lag_only, parse_args

csv.field_size_limit(10 ** 7)

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "stage0_output", "coding_sheet.csv")


def primary_denominator(rows):
    """Same selection as compute_outcome.py: coded, full text available,
    space = sensor or both."""
    out = []
    for r in rows:
        note = (r.get("coder_note") or "").lower()
        has_measure = any(flag(r, c) for c in ZERO_LAG + ROBUST) or \
                      (r.get("other_measure") or "").strip()
        space = (r.get("space") or "").strip()
        if "no-full-text" not in note and has_measure and space in ("sensor", "both"):
            out.append(r)
    return out


def cochran_armitage(denom, ppc_rule=True):
    by_year = defaultdict(lambda: [0, 0])
    for r in denom:
        y = int((r.get("year") or "").strip())
        by_year[y][1] += 1
        by_year[y][0] += zero_lag_only(r, ppc_rule)
    n = sum(nn for _, nn in by_year.values())
    k = sum(kk for kk, _ in by_year.values())
    pbar = k / n
    t = sum(x * (kk - nn * pbar) for x, (kk, nn) in by_year.items())
    var = pbar * (1 - pbar) * (sum(nn * x * x for x, (_, nn) in by_year.items())
                               - sum(nn * x for x, (_, nn) in by_year.items()) ** 2 / n)
    z = t / math.sqrt(var)
    return z, math.erfc(abs(z) / math.sqrt(2)), n


def main():
    path, ppc_rule = parse_args(sys.argv[1:], DEFAULT)
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    z, p, n = cochran_armitage(primary_denominator(rows), ppc_rule)
    print(f"Cochran-Armitage trend over year (primary denominator)   {path}")
    print(f"  PPC rule: {'on' if ppc_rule else 'off'}")
    print(f"  z = {z:.3f}")
    print(f"  p = {p:.3f}   (two-sided)")
    print(f"  n = {n}")


if __name__ == "__main__":
    main()
