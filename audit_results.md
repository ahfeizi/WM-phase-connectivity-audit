# Audit results and gate decision

Protocol: `audit_protocol.md` v1.2 (as amended by D9)
Final values (2026-10-17): 548 records screened, 101 included and coded (97 from
the main search and 4 recovered in D12). All values below are computed from
`coding_sheet_with_D12.csv` with the PPC rule on (D20). The full history of
changes, with before/after values, is in deviations.md (D1–D20).

---

## Primary outcome

Among included studies whose analysis space is sensor or both, the proportion
reporting **at least one** zero-lag-sensitive measure (PLV, coherence, phase
coherence) and **no** volume-conduction-robust companion (PLI, wPLI, dwPLI,
imaginary coherency, ciPLV):

> **41 / 83 = 0.494, 95% Wilson CI [0.389, 0.599]**

Without the PPC rule: 40 / 83 = 0.482 [0.378, 0.588].

Pool: 101 included records. R0295 (see below), R0055 (deviations.md, D11) and
R0386 (D19) were excluded at coding.

Sensitivity. The estimate is stable across every judgment call made in coding:
0.500 [0.395, 0.605] with R0295 retained, 0.500 [0.394, 0.606] with R0144
excluded, 0.506 [0.401, 0.611] with R0295 retained and R0144 excluded, 0.482
[0.378, 0.588] without the PPC rule, and 0.506 [0.400, 0.612] (41/81) without
the four D12 records. No conclusion here rests on a borderline decision.

## Subgroups

| Analysis space | zero-lag only | proportion | 95% CI |
|---|---|---|---|
| sensor or both (primary) | 41/83 | 0.494 | [0.389, 0.599] |
| source only | 12/18 | 0.667 | [0.437, 0.837] |

After D19 no record is coded `space = both`.

R0436 (`other_measure = PPC`, source) and R0575 (`other_measure = "PPC, CFC
coherence"`, sensor) carry no measure flag. PPC (pairwise phase consistency) is
an unbiased estimator of squared PLV, so `compute_outcome.py` counts both as
zero-lag-sensitive under the PPC rule (deviations.md, D20). Without the rule
(`--no-ppc-rule`) the primary outcome is 40/83 and the source-only subgroup
11/18.

Source-space studies are reported separately: leakage in source space is a
related but distinct problem, and the interval is too wide for comparison.

## Measure frequencies (all 101 coded records)

| Measure | n | Family |
|---|---|---|
| PLV | 35 | zero-lag-sensitive |
| coherence | 21 | zero-lag-sensitive |
| phase coherence | 1 | zero-lag-sensitive |
| PLI | 15 | robust |
| wPLI | 15 | robust |
| dwPLI | 8 | robust |
| imaginary coherency | 7 | robust |
| ciPLV | 0 | robust |

## Temporal trend

Cochran–Armitage test for trend over publication year, on the primary
denominator: z = −1.111, p = 0.267, n = 83 (`trend_test.py`). Without the PPC
rule: z = −1.205, p = 0.228. No evidence of change in reporting practice across
2015–2025. Year-by-year proportions range from 0.33 to 1.00 on denominators of
3 to 14, and the pattern is not monotonic.

---

## Gate decision (§8)

| Criterion | Threshold | Result | Met |
|---|---|---|---|
| 1. Eligible pool | ≥ 100 | 101 | yes |
| 2. Primary proportion | ≥ 0.60 | 0.494 [0.389, 0.599] | **no** |
| 3. Structure in a secondary question | CI excluding no effect | trend p = 0.267; sensor vs source CIs overlap heavily | **no** |
| 4. Non-obvious finding | ≥ 0.20 on 4a or 4b | not assessable — `cites_robust` coded on 3 of 101 records | **no** |
| 5. Novelty confirmed | mandatory | never verified | **no** |

The gate requires criterion 5 plus at least three of criteria 1–4. Only
criterion 1 is met, and only with the four D12 records (97 without them); the
mandatory criterion was never checked.

**The gate fails. No standalone review is written.** Per §8, the audit is
reported as one paragraph and one supplementary table in the introduction of the
empirical manuscript.

This is the pre-registered consequence of a pre-registered threshold, decided
before the number was known. The deferred variables remain codable from the same
record set if the decision is ever revisited.

---

## What the audit supports, and what it does not

**Supports.** Reporting only zero-lag-sensitive phase measures is roughly a
coin flip in this literature — about half of sensor-space EEG working-memory
connectivity studies published 2015–2025 report no volume-conduction-robust
companion measure. That is a sufficient and defensible motivation for a
methodological reanalysis: the practice the reanalysis examines is common, not
a straw man.

**Does not support.** Any claim that the field predominantly uses inadequate
measures: the point estimate is below 0.60 and the interval's upper bound
(0.599) falls just short of it. Nor any claim about change over time: there is
no trend. Nor any claim about citation versus practice: that variable is not
coded.

---

## Data-quality items

**Resolved by judgment.** Nine records carry
only an unnamed measure in `other_measure`. Classified as robust: R0005 (iPLV,
alongside cross-patch PLV), R0339 (lagged phase synchronisation), R0364 (lagged
linear coherence), R0424 and R0442 (phase slope index), R1011 (lagged linear
connectivity). Classified as zero-lag-sensitive by the PPC rule (D20): R0436 and
R0575 (pairwise phase consistency — a bias-corrected PLV estimator, still
zero-lag-sensitive). R0575 is the one record whose classification moves the
primary estimate (41/83 with the rule, 40/83 without). R0144: see below.

**Resolved.**

- **R0295**, *Ridge-penalized adaptive Mantel test and its application in
  imaging genetics* (Statistics in Medicine, 2021), coded `coh` / sensor.
  Excluded under `simulation`: a statistical-methods paper, with the EEG data
  serving as a demonstration rather than as a working-memory connectivity
  analysis.
- **R0144**, coded `other_measure = "CSD, SPACE-FSP"`. **Retained.** SPACE-FSP
  is the phase-coupling decomposition of van der Meij, Jacobs & Maris (Hum Brain
  Mapp 2015), which estimates phase relationships between sites and models
  site-specific phase explicitly. It is therefore an inter-regional phase
  measure and not zero-lag-sensitive. Counted as reporting a non-zero-lag
  measure, so it is in the denominator and not in the numerator. CSD in the same
  cell is the reference scheme, not a connectivity measure.
- **`space = both`.** All records coded `both` were checked at full text (D18,
  D19); none analyses connectivity in both sensor and source space, and each was
  recoded `sensor` or `source`.

**Not coded.** `cites_robust` carries a value on 3 of 101 records, and those
values are free text naming the cited authors rather than the specified 1/blank.
R0005's entry (`0 Nolte، Stam، Vinck`) is ambiguous. The column is reported as
not coded, and gate criterion 4 as not assessable.
