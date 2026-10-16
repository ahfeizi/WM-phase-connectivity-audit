# Reporting practices for phase-based connectivity in EEG working-memory research: a scoping audit

**Protocol version 1.0 — pre-registered before screening.**
Author: Amir Hossein Feizi (ORCID 0000-0001-8929-0910)

---

## 1. Rationale

Zero-lag-sensitive phase-synchrony indices — the phase-locking value (PLV), magnitude-squared
coherence, and related measures — cannot distinguish genuine inter-regional phase coupling from
volume conduction of a single source to multiple sensors. Volume-conduction-robust alternatives
(the phase-lag index family; imaginary coherency) have been available and implemented in standard
toolboxes since Nolte et al. (2004) and Stam et al. (2007), with the debiased weighted variant
introduced by Vinck et al. (2011).

Two reanalyses by the present author illustrate the consequences. In one, a spatially coherent
high-gamma frontoparietal PLV effect (N = 47) was corroborated by no volume-conduction-robust
index, failed multiple-comparison correction, collapsed under current source density
re-referencing, and carried a zero-lag phase-difference signature. In the other (N = 22), the
evidential status of a connectivity null shifted materially with the choice of spectral
decomposition.

Whether these are isolated cases or instances of a general reporting pattern is an empirical
question about the literature, and it has not been quantified. This audit addresses it.

## 2. Primary question

Among empirical human EEG studies reporting inter-regional phase-based connectivity during
working-memory tasks, what proportion report **only** zero-lag-sensitive measures, without any
volume-conduction-robust companion measure?

## 3. Secondary questions

1. Does that proportion change across publication year?
2. Does it differ between sensor-space and source-space analyses?
3. What reference schemes are used, and how often is the scheme left unstated?
4. Among studies that cite Nolte et al. (2004) or Vinck et al. (2011), what proportion nonetheless
   report only zero-lag-sensitive measures?
5. How often is volume conduction acknowledged in the text without any analytic response?

## 4. Databases and search

PubMed (via NCBI E-utilities) and Europe PMC (via REST API). Both are openly accessible; no
subscription database is used. This is a stated limitation: coverage of engineering and
conference literature indexed only in Web of Science or Scopus is incomplete.

Search executed once, on a single date, and the date recorded. No hand-searching of reference
lists at Stage 0.

**Query concepts (full strings in `stage0_search.py`):**

- Modality: EEG / electroencephalograph*
- Task domain: working memory / n-back / Sternberg / delayed match / short-term memory
- Measure: phase locking / PLV / coherence / phase synchrony / phase lag index / wPLI / dwPLI /
  imaginary coherence / phase coupling / phase connectivity
- Filters: 2015–2025, human, English

## 5. Eligibility

**Include** if all of the following hold:

1. Empirical study in human participants.
2. Scalp EEG is the connectivity modality.
3. At least one inter-electrode or inter-region phase-based connectivity measure is reported.
4. Connectivity is computed during a working-memory task (encoding, maintenance, retrieval, or
   task-versus-baseline contrasts anchored to a working-memory paradigm).
5. Published 2015–2025, in English, full text obtainable.

**Exclude** if any of the following hold:

1. Review, meta-analysis, commentary, editorial, protocol, or conference abstract.
2. Simulation or methods-development paper with no empirical working-memory application.
3. MEG-only, intracranial-only, fNIRS-only, or animal study. (Studies reporting both EEG and
   another modality are included, and coded on their EEG analysis.)
4. Resting-state connectivity only, with no task-based connectivity contrast.
5. Amplitude- or power-based connectivity only (e.g. power envelope correlation) with no
   phase-based measure.
6. Within-channel cross-frequency coupling only (e.g. phase–amplitude coupling), with no
   inter-region phase measure.
7. N < 10 in the analysed sample.

## 6. Screening procedure

Title and abstract screening, then full-text screening against the criteria above.

Single-screener coding is the default and is reported as a limitation. A second screener will
independently code a random 20% subset; Cohen's kappa is reported for the primary eligibility
decision and for the primary coded variable. If kappa < 0.70 on either, the coding manual is
revised and the full set re-screened.

Screening decisions and exclusion reasons are logged per record. A PRISMA-ScR flow diagram is
produced.

## 7. Coded variables

| # | Variable | Values |
|---|----------|--------|
| 1 | Connectivity measures reported | multi-select: PLV; coherence; phase coherence; PLI; wPLI; dwPLI; imaginary coherency; ciPLV; other (specify) |
| 2 | Analysis space | sensor; source; both |
| 3 | Reference scheme | average; linked mastoids/earlobes; single electrode; CSD/Laplacian; REST; other; not stated |
| 4 | Volume conduction in text | addressed analytically; acknowledged only; not mentioned |
| 5 | Cites Nolte 2004 or Vinck 2011 | neither; one; both |
| 6 | Publication year | integer |

**Primary outcome:** proportion of included studies whose reported measures (variable 1) are
exclusively zero-lag-sensitive (PLV, coherence, phase coherence) **and** whose analysis space
(variable 2) includes sensor space.

Proportions are reported with 95% Wilson confidence intervals. No study is named individually in
the text; results are reported as aggregate counts only.

## 8. Stop rules, fixed in advance

These thresholds are committed to before any screening. They determine whether the audit becomes
a standalone review or remains a subsection of the empirical manuscript.

**Gate criterion 5 is mandatory. At least three of criteria 1–4 must also hold.**

1. Eligible pool ≥ 100 included studies.
2. Primary outcome proportion ≥ 0.60.
3. At least one secondary question shows structure — a monotonic trend across year, or a
   difference between sensor and source space, with a 95% CI excluding no effect.
4. At least one non-obvious finding, defined in advance as either: (a) ≥ 20% of included studies
   cite Nolte 2004 or Vinck 2011 while reporting only zero-lag-sensitive measures, or (b) ≥ 20%
   acknowledge volume conduction in the text without any analytic response.
5. Novelty confirmed: no published audit quantifying phase-connectivity reporting practice in this
   or an adjacent cognitive domain.

**If the gate is not passed:** the audit is reported as a single paragraph and one supplementary
table in the introduction of the empirical manuscript, and no standalone review is written.

**Hard time limit:** Stage 0 (search and count only) is capped at two days. Stage 1 (piloted
coding of a random sample of 50 records) is capped at two weeks. Neither cap is extended.

## 9. Deviations

Any deviation from this protocol is logged with its date and reason in `deviations.md` in the
project repository, and reported in the manuscript.
