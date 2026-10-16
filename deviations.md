# Deviations from the pre-registered protocol

Protocol: audit_protocol.md v1.0
Screening manual: screening_manual.md v1.0

---

## D1 — Search query broadened (2026-09-09)

**What changed.** The MEASURE block was restricted to named connectivity
indices in title/abstract. It was replaced with the general terms
`connectivity`, `synchron*`, `coupling`, `coherence` alongside the named
indices.

**Why.** Papers that report a phase-synchrony index as a secondary analysis
typically name it only in the methods, not the abstract. The original block
therefore selected papers where connectivity is the headline finding — the
subset most likely to have used robust measures. This biased the sample toward
better practice and would have underestimated the primary outcome.

**Effect.** PubMed hits rose from 112 to 546.

---

## D2 — `humans[mh]` filter removed (2026-09-09)

**What changed.** The MeSH human filter was dropped from the query.

**Why.** MeSH indexing lags publication by several months, so 2025 records were
systematically excluded — precisely the year needed for the temporal-trend
analysis. Non-human studies are removed at screening instead.

---

## D3 — PubMed DOI extraction was faulty (2026-09-18)

**What happened.** `stage0_search.py` extracted DOIs with
`art.findall(".//ArticleId")`. The descendant axis reaches into
`<ReferenceList>`, so the match was the ArticleId of a *cited reference*, not of
the article. The last match won, giving each PubMed record the DOI of the final
entry in its own bibliography.

**Scope.** 226 of 519 PubMed records (43.5%) carried an incorrect DOI. Four
records had no retrievable DOI.

**How it was found.** Deduplication produced 667 unique records where an earlier
run of the same search had produced 548. Inspection of the mismatch showed
record pairs with identical titles and identical abstracts but unrelated DOIs.

**Consequences.** DOI-based deduplication never matched, leaving 136 duplicate
pairs in the sheet. These were labelled independently by the pre-screening pass
and merged afterwards on normalised title.

**Repair.** `fix_dois.py` re-fetched each DOI by PMID, scoped to
`PubmedData/ArticleIdList` with `ELocationID` as fallback, then merged the
remaining duplicates. Unique records: 530. No label was altered.

**Unintended benefit.** Because the 136 duplicate pairs were labelled twice
without the pass knowing they were the same paper, their agreement is a
within-rater consistency estimate for the pre-screening tool: 136/136 (100%).
This is reported as consistency, not accuracy.

---

## D4 — Screening rules not anticipated by the manual (2026-09-18; text completed 2026-10-16)

The screening manual did not cover two eligibility questions.

**Mental arithmetic.** Eligible when the study manipulated working-memory load
(for example, parametric difficulty) or explicitly modelled the task as a
working-memory process. Not eligible when arithmetic served as a generic workload
or stress induction contrasted with rest. This rule is consistent with the
treatment of R0223 (D8): a task is eligible only if it manipulates working memory,
not merely if working memory is involved. The rule was written down only after
coding (see D11).

**Phase transfer entropy.** No PTE study reached the coding stage. The two
screened records reporting PTE (R0212, R0278) were excluded at screening as
`classification-only`: PTE served only as a classifier feature. No
`directed/other` category was created, and the earlier text of this entry, which
described one, was incorrect.

---

## D5 — Accuracy sample drawn after the sheet had been opened (2026-09-18)

The blind accuracy sample was drawn after the author had opened the screening
file, though no `rec_id` or label had been read. Blinding is therefore asserted
rather than procedurally guaranteed. Stated in the limitations.

---

## D6 — Publication-year inconsistencies (2026-09-18; corrected 2026-10-16)

Three records fell outside the 2015–2025 window (one 2026, two 2014), arising
from disagreement between `ArticleDate` (online-first) and `PubDate` (issue).
Records affected: R0001, R0518, R0519. Outcome: not removed. All three were
screened and excluded on other grounds: R0001 `classification-only`, R0518
`no-phase-connectivity`, R0519 `classification-only`. No out-of-window rule was
needed to exclude them. The earlier text of this entry, which stated that an
out-of-window rule was adopted and the records removed, was incorrect.

## D7 — Screening manual revised after the first accuracy assessment (2026-10-02)

**Trigger.** A blind 50-record accuracy assessment returned Cohen's kappa 0.28.
Inspection of the confusion matrix showed the low value did not come from
include/exclude disagreement: on the 33 records where both raters gave a
definite label, agreement was 32/33. All of the loss came from inconsistent use
of the `?` category — the author used it as a "check later" marker, the
pre-screening pass as "the abstract cannot settle eligibility".

**Change 1.** The `?` definition was tightened: it now applies only when the
connectivity measure is unspecified and all other conditions are met. A plainly
violated condition yields `0` even when the abstract contains a connectivity
word.

**Change 2.** A new exclusion code `classification-only` was added, for studies
in which a phase-based measure serves only as a classifier feature with no
inferential claim about connectivity. This rule was applied implicitly by the
author during the accuracy sample (records R0445, R0620) and was absent from the
manual.

**Consequence.** The first accuracy assessment is reported as a pilot that
identified an ambiguity in the manual, not as the accuracy estimate for the
method. A second blind sample was drawn under the revised manual, with a new
random seed, and that estimate is the one reported.

**Procedural note.** During the first sample, labels were revised between two
scoring runs, producing two kappa values (0.235 and 0.281). For the second
sample, labels are fixed before scoring and scored once.

## D8 — Second accuracy assessment (2026-10-02)

**Procedure.** A second blind sample of 50 records was drawn from
screening_sheet_final.csv with a new random seed (20261002) under the revised
screening manual. The author coded all 50 without sight of the pre-screening
labels, then scored once.

**Result.** Observed agreement 0.900 (45/50), chance agreement 0.534,
**Cohen's kappa = 0.785**. This is the accuracy estimate reported for the
pre-screening pass.

The `?` category, which caused the failure of the first assessment, showed
complete agreement (7/7) under the revised definition.

**Disagreements and their resolution** (5 records):

- R0014 — author `1`, model `?`. Resolved as `?`: the connectivity measure is
  not named in the abstract and all other conditions are met, so the revised
  rule applies.
- R0017 — author `0` (`resting-only`), model `1`. Full text: wPLI was computed
  on task-period / data. Resolved as `1`.
- R0223 — author `0` (`no-WM`), model `?`. Resolved as `0`: the retention
  interval is incidental to a self-touch paradigm, not a working-memory
  manipulation.
- R0489 — author `0` (`classification-only`), model `?`. Resolved as `0`: a
  network-thresholding method paper, excluded under `simulation`.
- R0514 — author `1`, model `0`. Full text: the phase-locking index was
  computed across trials at single electrodes. Resolved as `0`.

**Procedural note.** After inspecting the disagreements the author revised the
sample labels and re-scored, yielding kappa 0.914. That value is an artefact of
deliberate convergence and is not reported. The reported estimate is the 0.785
obtained from the single blind coding pass, consistent with the procedure fixed
in D7.

## D9 — Audit narrowed to the primary outcome (2026-10-09)

**Screening result.** 530 unique records screened on title and abstract, then at
full text where the abstract was indeterminate. 100 included, 430 excluded.
Of the 73 records the pre-screening pass labelled `?`, 47 were included after
full-text screening and 26 excluded — so nearly half the included pool comes
from full-text screening, and the pre-screening pass was substantially
conservative rather than permissive.

**Gate criterion 1 (§8).** Eligible pool ≥ 100: met, at exactly 100. Criteria
2–4 depend on the coding stage and were not assessable at this point.

**Amendment.** Coding is narrowed to the variables required for the primary
outcome: connectivity measures reported, and analysis space. Three variables
from §7 are deferred and not coded: reference scheme, whether volume conduction
is addressed in the text, and the citation-versus-practice contrast. Citation of
Nolte (2004), Stam (2007) or Vinck (2011) is recorded opportunistically where
the PDF is searchable, with the checked subset as its denominator.

**Consequence.** The audit is reported as a motivating paragraph and one
supplementary table in the empirical manuscript. No standalone review is
written. The deferred variables remain codable from the same record set if that
decision is revisited.

**Reason.** The full six-variable coding of 100 full texts is 15–25 hours and
requires a second coder for the eligibility kappa. The empirical manuscript —
which the audit exists to motivate — is unwritten. Narrowing the audit buys the
one number the manuscript needs at roughly a third of the cost, and leaves the
full audit available later, when a published empirical paper would lend it
standing it does not currently have.

**Record corrections.** Two `exclusion_reason` values were malformed and were
corrected without changing any eligibility decision: R0493 `opinion paper` →
`review`, R0012 `no-phase-connectivit` → `no-phase-connectivity`.

**Statistic not reported.** Agreement between `ai_label` and the author's
`include` decision was 448/457 (98.0%) on records the pre-screening pass labelled
definitively, kappa 0.906. The author saw the pre-screening labels during that
review, so this is verification-pass agreement, not an inter-rater statistic.
The reported accuracy estimate for the pre-screening pass remains the kappa of
0.785 from the blind sample (D8).

## D10 — Coding complete; gate applied and failed (2026-10-09)

**Result.** 100 records coded on the narrowed variable set; one subsequently
excluded (below), leaving a pool of 99. Primary outcome: 44 of 85 sensor-space
or mixed-space studies (0.518, 95% Wilson CI [0.413, 0.621]) report only
zero-lag-sensitive phase measures with no volume-conduction-robust companion.

**Two records reconsidered at the coding stage.**

- **R0295** (*Ridge-penalized adaptive Mantel test and its application in
  imaging genetics*, Statistics in Medicine, 2021) is excluded under
  `simulation`. It is a statistical-methods paper in which the EEG data serve as
  a demonstration rather than as a working-memory connectivity analysis. This
  reverses an inclusion decision made at screening.
- **R0144** (`other_measure = "CSD, SPACE-FSP"`) is retained. SPACE-FSP is the
  phase-coupling decomposition of van der Meij, Jacobs & Maris (Human Brain
  Mapping, 2015), which estimates phase relationships between recording sites
  and models site-specific phase explicitly; it is an inter-regional phase
  measure and is not zero-lag-sensitive. CSD in the same cell is the reference
  scheme, not a connectivity measure. An earlier reading of this cell took
  SPACE-FSP for a decomposition carrying no connectivity estimate and proposed
  exclusion; that reading was wrong and was corrected before the record was
  dropped.

**Gate (§8).** Criterion 1 not met (pool 99 against a threshold of 100).
Criterion 2 not met (0.518 against 0.60). Criterion 3 not met (Cochran–Armitage
trend over year z = −1.315, p = 0.188; sensor-versus-source intervals overlap
heavily). Criterion 4 not assessable: `cites_robust` carries a value on 3 of 100
records and those values are free text rather than the specified coding, so the
citation-versus-practice contrast cannot be computed. Criterion 5, which is
mandatory, was never verified.

None of the four discretionary criteria met, and the mandatory criterion
unchecked. **The gate fails.** The audit is reported as one paragraph and one
supplementary table in the introduction of the empirical manuscript; no
standalone review is written.

**Note on the direction of the finding.** The threshold of 0.60 was fixed before
the search was run and before any screening. The observed proportion falls below
it, and the audit is reported accordingly: as evidence that the practice under
examination is common — roughly half the sensor-space literature — rather than
as evidence that it predominates. The pre-registered threshold was not revised
after the estimate was known.

**Sensitivity.** The estimate is stable across every judgment call in coding:
0.523 [0.419, 0.626] with all 100 records, 0.518 [0.413, 0.621] with R0295
excluded, 0.524 [0.418, 0.627] with both R0295 and R0144 excluded. Seven records
carried only an unnamed measure in `other_measure` and were classified by
measure family (R0005 iPLV alongside cross-patch PLV, R0339 lagged phase
synchronisation, R0364 lagged linear coherence, R0424 and R0442 phase slope
index, R0144 SPACE-FSP — all non-zero-lag; R0436 pairwise phase consistency, a
bias-corrected PLV estimator and therefore zero-lag-sensitive). The primary
estimate is unchanged whether these are classified or left out.

**Possible column misuse, not resolved.** `space = both` may have been entered
for multi-modality rather than sensor-plus-source in R0101 (EEG + fMRI), R0434
(EEG + NIRS) and R0580 (scalp + invasive EEG). The primary estimate is
unaffected, since `both` and `sensor` enter the same denominator; the
source-space subset would change if these are reclassified.

---

## D11 — Mental-arithmetic rule applied after coding (2026-10-16)

**What happened.** The D4 rule for mental arithmetic was never written at
screening. It was formulated after the primary outcome was known, on review of
the four included records whose abstracts mention arithmetic:

| Record | Task | Decision |
|---|---|---|
| R0663 | Mental summation at five parametric difficulty levels, explicitly modelled as working memory (central executive and storage buffer) | Retained |
| R0055 | Serial subtraction as a stress/workload induction, task versus rest, no load manipulation | Excluded (`no-WM`) |
| R0247, R0261 | Arithmetic mentioned in the abstract only; the analysed task is a working-memory task | Unaffected |

**Effect on the primary outcome.**

| | Primary outcome |
|---|---|
| Before | 44/85 = 0.518, 95% Wilson CI [0.413, 0.621] |
| After | 43/84 = 0.512 [0.407, 0.616] |

Cochran–Armitage trend over publication year: z = −1.431, p = 0.153, n = 84.

No gate criterion or conclusion changes. Both values are reported, and the
earlier value is retained in this record.

**Why this is a deviation, not a correction.** The rule was applied with the
outcome known. Its direction of effect is small and reduces the numerator, but
it is disclosed as a post-hoc decision.

Pool after D11: 98 included records (D10: 99, minus R0055). R0295 (D10) and
R0055 (D11) are now recorded as excluded in screening_sheet_final.csv and
removed from coding_sheet.csv; compute_outcome.py and trend_test.py reproduce
all reported values from the sheets.

The source-only subgroup reads 8/14 from the flag columns; with R0436 (PPC)
classified as zero-lag-sensitive as in D10 it is 9/14. The primary outcome is
unaffected (R0436 is source-only).

---

## D12 — Records lost at retrieval and deduplication (2026-10-16)

Identified during manuscript preparation.

**What happened.** Two retrieval errors removed eligible records before
screening.

- *Faulty-DOI collisions in stage-0 deduplication.* Deduplication matched
  records on PubMed DOIs that were themselves faulty (D3), so distinct papers
  sharing a faulty DOI were merged as duplicates. Stage-0 deduplication dropped
  27 PubMed records: 26 through faulty-DOI collisions with unrelated papers, and
  one (R1013) as an exact title match with its own published version (R0098),
  which is a correct merge. Of the 26, 12 entered the screened set through
  Europe PMC rows; 14 were never screened. 5 Europe PMC records were also dropped
  through faulty-DOI collisions; of these, 3 were screened through their own
  PubMed rows and 2 are the D12 PubMed records 38678958 (R1014) and 26638838
  (R1003).
- *Europe PMC wildcard removal.* `stage0_search.py` builds the Europe PMC query
  with `_epmc_block`, which strips every `*` (`t.replace("*", "")`). Truncated
  stems such as `electroencephalogra*` and `synchron*` were therefore sent as
  literal fragments, and records matching only through truncation were not
  retrieved. 4 Europe PMC-only records (R1016–R1019) were lost this way
  (`epmc_truncation`).

**Scope.** 18 records eligible for screening were lost: 14 PubMed records
through faulty-DOI collisions and the 4 Europe PMC-only records through wildcard
removal. The 5 Europe PMC collision drops add no records beyond these 18. The
lost records were screened as R1001–R1019 in `stage0_output/D12/` (19 records:
the 18 lost records and R1013, a preprint of R0098, excluded as `duplicate`).
At title/abstract screening, four were included (R1004, R1005, R1008, R1011);
all four were confirmed eligible at full text and coded; the outcome with and
without them is below.

**Effect on the primary outcome.**

| | Before | After |
|---|---|---|
| Primary outcome | 43/84 = 0.512, 95% Wilson CI [0.407, 0.616] | 43/86 = 0.500 [0.397, 0.603] |
| Source-only, flag columns | 8/14 | 9/16 |
| Source-only, R0436 (PPC) as zero-lag-sensitive | 9/14 | 10/16 |

Cochran–Armitage trend over publication year: before z = −1.431, p = 0.153,
n = 84; after z = −1.175, p = 0.240, n = 86.

Before = `coding_sheet.csv`; after = `coding_sheet_with_D12.csv` (the same
sheet plus the four D12 records), both computed with compute_outcome.py and
trend_test.py.

---

## D13 — Search executed more than once (2026-10-16)

Identified during manuscript preparation.

**Protocol.** §4: "Search executed once, on a single date, and the date
recorded."

**What happened.** The search was executed more than once. Documented runs:

- the runs before and after the query amendments of D1 and D2 (PubMed hits
  112 → 546);
- the earlier run whose deduplicated count (548) is the comparison point in D3;
- the final run of 2026-09-18, saved in `screening_sheet_raw.csv`, which is the
  screened record set.

The total number of executions was not recorded.

---

## D14 — Second-screener procedure not followed (2026-10-16)

Identified during manuscript preparation.

**Protocol.** §6: a second screener independently codes a random 20% subset;
Cohen's kappa is reported for the primary eligibility decision and for the
primary coded variable; if kappa < 0.70 on either, the coding manual is revised
and the full set re-screened.

**What happened.**

- There was no second human screener. Instead, the author's labels were compared
  with the LLM pre-screening labels on blind samples of 50 records (9.4% of
  530; D7, D8), rather than a second screener coding 20%.
- No kappa was computed for the primary coded variable.
- After the first kappa of 0.28 (D7) the manual was revised, but the full set was
  not re-screened; a second blind sample was drawn instead (D8).

The reported kappa (0.785, D8) is agreement between the author and the
pre-screening pass, not between two human screeners.

---

## D15 — No PRISMA-ScR flow diagram (2026-10-16)

Identified during manuscript preparation.

**Protocol.** §6: "A PRISMA-ScR flow diagram is produced."

**What happened.** No flow diagram was produced at the time. One will be
produced for the manuscript.

---

## D16 — Stage time caps exceeded (2026-10-16)

Identified during manuscript preparation.

**Protocol.** §8: Stage 0 (search and count only) is capped at two days, Stage 1
at two weeks, and "Neither cap is extended."

**What happened.** Both caps were exceeded. Stage 0 entries in this log run from
2026-09-09 (D1, D2) to 2026-09-18 (D3, D5, D6), and Stage 0 retrieval was
reopened for D12. Screening and coding ran from 2026-09-18 to 2026-10-09 (D10).

Dates are taken from log entries, not from a timesheet. Stage 1 (piloted coding
of 50 records) was not run in the form the protocol specified.

---

## D17 — Protocol version labels (2026-10-16)

Identified during manuscript preparation.

Project files carry protocol version labels: "v1.1" in `queries.json`
(`"protocol_version": "1.1"`) and `stage0_search.py`, and "v1.2" in
`audit_results.md`.

"v1.1" denotes the query after D1 and D2. "v1.2" denotes the protocol as
amended by D9; whether the label was meant to include D1–D2 is not recorded.
Neither label corresponds to a separate protocol document; `audit_protocol.md`
v1.0 is the only protocol text.

---

## D18 — R0261 analysis space and R0223 exclusion reason corrected (2026-10-16)

Identified during reconciliation of the PRISMA counts.

**R0261: `space` both → source.** Inter-regional theta PLV (bilateral IPS seed
to whole brain) was computed from EEG source maps only (Results p. 2; Methods,
Functional connectivity). The sensor-level analyses were power and
stimulus-to-brain PLV, which is not inter-regional. MEG (experiment 1) was used
only for stimulus-to-brain PLV. D10 noted that `both` may have been entered for
multiple modalities (EEG plus fMRI, NIRS or invasive EEG) rather than for sensor
plus source analysis in R0101, R0434 and R0580, and left this unresolved; R0261
(MEG plus EEG) is a confirmed case of the same kind. All remaining `both`
records are checked in D19.

R0261 reports PLV with no robust index, so it leaves both the numerator and the
denominator of the primary outcome and enters the source-only subgroup.

| | Before | After |
|---|---|---|
| Primary outcome, without D12 | 43/84 = 0.512, 95% Wilson CI [0.407, 0.616] | 42/83 = 0.506 [0.401, 0.611] |
| Primary outcome, with D12 | 43/86 = 0.500 [0.397, 0.603] | 42/85 = 0.494 [0.390, 0.598] |
| Source-only, flag columns, without D12 | 8/14 | 9/15 |
| Source-only, flag columns, with D12 | 9/16 | 10/17 |
| Source-only, R0436 (PPC) as zero-lag-sensitive, without D12 | 9/14 | 10/15 |
| Source-only, R0436 (PPC) as zero-lag-sensitive, with D12 | 10/16 | 11/17 |

Cochran–Armitage trend over publication year: without D12, z = −1.431,
p = 0.153, n = 84 before and z = −1.477, p = 0.140, n = 83 after; with D12,
z = −1.175, p = 0.240, n = 86 before and z = −1.224, p = 0.221, n = 85 after.

**R0223: `exclusion_reason` no-phase-connectivity → no-WM**, matching the
resolution recorded in D8 (the retention interval is incidental to a self-touch
paradigm, not a working-memory manipulation). The include decision (0) is
unchanged.

**Files.** Pre-change copies are kept in `stage0_output/` as
`coding_sheet_pre_D18.csv`, `screening_sheet_final_pre_D18.csv`,
`coding_sheet_with_D12_pre_D18.csv` and `screening_sheet_with_D12_pre_D18.csv`.
The two `_with_D12` sheets were rebuilt from the corrected sheets. The D12 table
records the values before this correction.

---

## D19 — Remaining `space = both` records checked; R0386 excluded at coding (2026-10-16)

Identified during reconciliation of the PRISMA counts.

The six records still coded `space = both` after D18 were checked at full text.
None analyses connectivity in both sensor and source space. This resolves the
question D10 left open for R0101, R0434 and R0580: all three are sensor-space.

| Record | Change | Reason |
|---|---|---|
| R0434 (Gao, J Biophotonics) | `space` both → sensor | Coherence between 34 scalp electrodes; no source analysis. |
| R0580 (Riddle, J Neurosci) | `space` both → sensor; `PSI` removed from `other_measure` | wPLI on scalp EEG only; PSI was computed on invasive EEG only. |
| R0256 (Ratcliffe, Curr Biol) | `space` both → sensor; `plv` 1 → 0 | Coherence from Fz to all channels; no source analysis; the paper reports coherence only. |
| R0101 (Zhang & Yu, PLoS Biol) | `space` both → sensor; `wpli = 1`, `coh = 0` confirmed (already so coded) | Methods: "We chose the metric of weighted phase lag index". |
| R0506 (Chou, PLoS One) | `space` both → source; `coh = 1`, `plv = 1` confirmed (already so coded) | Connectivity between dipole-localized ICA component clusters. |
| R0386 (Fleischmann, Pilot Feasibility Stud) | excluded at coding: `include` 1 → 0, `exclusion_reason` → `resting-only`; removed from `coding_sheet.csv` | Resting-state EEG, no working-memory task. |

Each changed coding row carries a one-sentence `coder_note` giving the reason.
R0386 is excluded at coding as R0295 (D10) and R0055 (D11) were; before this
change its screening row carried `include = 1` together with
`exclusion_reason = no-WM`.

**Effect.** R0506 reports PLV and coherence with no robust index, so it leaves
both the numerator and the denominator of the primary outcome and enters the
source-only subgroup. R0386 reports wPLI and ImC, so it leaves the denominator
only. The other four stay in the primary denominator, which `sensor` and `both`
enter alike.

| | Before | After |
|---|---|---|
| Primary outcome, without D12 | 42/83 = 0.506, 95% Wilson CI [0.401, 0.611] | 41/81 = 0.506 [0.400, 0.612] |
| Primary outcome, with D12 | 42/85 = 0.494 [0.390, 0.598] | 41/83 = 0.494 [0.389, 0.599] |
| Source-only, flag columns, without D12 | 9/15 | 10/16 |
| Source-only, flag columns, with D12 | 10/17 | 11/18 |
| Source-only, R0436 (PPC) as zero-lag-sensitive, without D12 | 10/15 | 11/16 |
| Source-only, R0436 (PPC) as zero-lag-sensitive, with D12 | 11/17 | 12/18 |

Cochran–Armitage trend over publication year: without D12, z = −1.477,
p = 0.140, n = 83 before and z = −1.374, p = 0.169, n = 81 after; with D12,
z = −1.224, p = 0.221, n = 85 before and z = −1.111, p = 0.267, n = 83 after.

Pool after D19: 97 included records (D18: 98, minus R0386); 101 with D12. No
record is now coded `space = both`.

**Files.** Pre-change copies are kept in `stage0_output/` as
`coding_sheet_pre_D19.csv`, `screening_sheet_final_pre_D19.csv`,
`coding_sheet_with_D12_pre_D19.csv` and `screening_sheet_with_D12_pre_D19.csv`.
The two `_with_D12` sheets were rebuilt from the corrected sheets.

---

## D20 — R0575 measure coding corrected; PPC classification rule; verification sample (2026-10-17)

Identified in the random full-text verification sample.

**Verification sample.** Ten included records were drawn for full-text
verification (`stage0_output/verification_sample.csv`; draw procedure in
`verification_sample_README.md`): seed 20261016, a frame of 90 records (the 101
included records after D19, with D12, minus the 11 already checked at full
text), 10 drawn. The stopping rule was fixed before the sample was checked:
errors found in the sample are corrected and the error rate is reported, with no
further full re-check of the sheet.

| Check | Errors |
|---|---|
| Eligibility | 0/10 (95% Wilson CI [0.000, 0.278]) |
| Measure fields | 1/10 (R0575; [0.018, 0.404]) |
| Analysis space | 0/10 ([0.000, 0.278]) |
| Primary-outcome classification | 0/10 ([0.000, 0.278]) |

Record-level results are in `stage0_output/verification_sample_results.csv`.
R0144 (`other_measure = "CSD, SPACE-FSP"`) was confirmed as coded, consistent
with D10. The classification count of 0 holds with the PPC rule below. Without
it, correcting R0575 would move the record out of the numerator.

**R0575 (Neurodynamic correlates for cross-frequency coupled tACS): `coh`
1 → 0.** The inter-regional measure is PPC between frontal and
parieto-occipital electrodes. The "coherence" in the paper is within-channel
cross-frequency (phase-amplitude) coherence, not inter-regional coherence.
`other_measure` stays "PPC, CFC coherence", and `space` stays `sensor`. The
coding row carries this reason in `coder_note`.

**PPC classification rule.** PPC (pairwise phase consistency) is an unbiased
estimator of squared PLV (Vinck et al., 2010), so it is zero-lag-sensitive. PPC
has no flag column. D10 classified R0436 (`other_measure = PPC`) as
zero-lag-sensitive by hand, and D12, D18 and D19 reported that classification as
a separate source-only row. `compute_outcome.py` now applies it as an explicit
rule: a record whose `other_measure` contains "PPC" counts as having a
zero-lag-sensitive measure. The rule is on by default, and `--no-ppc-rule` turns
it off. `trend_test.py` imports the same rule and takes the same switch. With
the rule off, both scripts reproduce their earlier output on the pre-D20 sheets
exactly. Only R0436 and R0575 contain "PPC".

**Effect.** R0575 (sensor space, no robust index) stays in the primary
denominator either way. With the PPC rule it stays in the numerator; without the
rule it leaves the numerator. R0436 affects only the source-only subgroup.

| | Before (after D19) | After, PPC rule on | After, PPC rule off |
|---|---|---|---|
| Primary outcome, without D12 | 41/81 = 0.506, 95% Wilson CI [0.400, 0.612] | 41/81 = 0.506 [0.400, 0.612] | 40/81 = 0.494 [0.388, 0.600] |
| Primary outcome, with D12 | 41/83 = 0.494 [0.389, 0.599] | 41/83 = 0.494 [0.389, 0.599] | 40/83 = 0.482 [0.378, 0.588] |
| Source-only, without D12 | 10/16 (flag columns); 11/16 (R0436 as zero-lag-sensitive) | 11/16 | 10/16 |
| Source-only, with D12 | 11/18 (flag columns); 12/18 (R0436 as zero-lag-sensitive) | 12/18 | 11/18 |

Cochran–Armitage trend over publication year: before, z = −1.374, p = 0.169,
n = 81 without D12 and z = −1.111, p = 0.267, n = 83 with D12. After, with the
PPC rule, the values are unchanged. After, without the rule, z = −1.462,
p = 0.144, n = 81 without D12 and z = −1.205, p = 0.228, n = 83 with D12. Gate
criterion 2 (≥ 0.60) is not met under any of these.

**Files.** Pre-change copies are kept in `stage0_output/` as
`coding_sheet_pre_D20.csv` and `coding_sheet_with_D12_pre_D20.csv`. D20 changes
no screening sheet. The two `_with_D12` sheets were rebuilt from the corrected
sheets, and `screening_sheet_with_D12.csv` came out byte-identical, so it has no
pre-D20 copy. `compute_outcome.py` and `trend_test.py` were changed as described
above, and `verification_sample_results.csv` is new.
