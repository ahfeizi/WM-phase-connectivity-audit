# Phase-connectivity reporting audit: EEG working-memory studies, 2015–2025

How often do sensor-space EEG working-memory studies report only
zero-lag-sensitive phase measures (PLV, coherence) with no
volume-conduction-robust companion (PLI family, imaginary coherency)?

## Result

41/83 = 0.494 (95% Wilson CI 0.389–0.599) of sensor-space studies; 40/83 = 0.482
(0.378–0.588) without the PPC rule (deviations.md, D20). Source space, reported
separately: 12/18 (11/18 without the PPC rule). Cochran–Armitage trend over
2015–2025: z = −1.111, p = 0.267, n = 83. The pre-registered gate (§8) was not
met; see audit_results.md.

## Search

PubMed and Europe PMC, title/abstract, publication years 2015–2025, English;
run 2026-09-18. Exact queries and hit counts: stage0_output/queries.json.
546 PubMed + 306 Europe PMC hits → 530 unique records after deduplication and
DOI repair (deviations.md, D3), plus 18 records lost to two retrieval errors
and screened afterwards (D12) → 548 screened → 101 included and coded.

## Files

- audit_protocol.md, screening_manual.md: pre-registered protocol and screening rules
- deviations.md: every departure from the protocol (D1–D20), with before/after values
- audit_results.md: final results and the gate decision
- stage0_output/screening_sheet_final.csv: the 530 records from the main search,
  with IDs (PMID / Europe PMC), DOI, title, pre-screening label, and the
  authoritative human decision and exclusion reason
- stage0_output/screening_sheet_with_D12.csv: the same plus the 19 D12 rows
  (18 recovered records and one duplicate), 548 screened records in all
- stage0_output/D12/: the D12 screening and coding sheets on their own
- stage0_output/coding_sheet.csv: coding of the 97 included records from the
  main search; coding_sheet_with_D12.csv adds the 4 D12 records (101)
- stage0_output/coding_sheet*_pre_D*.csv: each coding sheet as it stood before
  the deviation named in the file
- stage0_output/kappa_sample.csv, kappa_key.csv, kappa_sample_run0710.csv,
  kappa_key_run0710.csv: the two screening-accuracy samples and their keys
  (D5, D7, D8)
- stage0_output/verification_sample.csv, verification_sample_results.csv,
  verification_sample_README.md: random full-text verification sample (D20)
- compute_outcome.py, trend_test.py: reproduce every reported number from the sheets
- stage0_search.py, dedupe_check.py, fix_dois.py, kappa_sample.py: search and
  screening pipeline, included for provenance

## Reproduce

From this folder (Python 3, standard library only):

    python compute_outcome.py stage0_output/coding_sheet_with_D12.csv
    python compute_outcome.py stage0_output/coding_sheet_with_D12.csv --no-ppc-rule
    python trend_test.py stage0_output/coding_sheet_with_D12.csv
    python trend_test.py stage0_output/coding_sheet_with_D12.csv --no-ppc-rule

Run the same commands on stage0_output/coding_sheet.csv for the values without
the D12 records (41/81 = 0.506 with the PPC rule).

## Not included

- Abstracts are not redistributed: the abstract column is removed from every
  sheet. Retrieve abstracts by PMID or DOI.
- No PDFs or full texts of the included papers.
- Superseded intermediate sheets (the raw, deduplicated and pre-deviation
  screening sheets), which carry abstracts.

The pipeline scripts are included for provenance. dedupe_check.py, fix_dois.py
and kappa_sample.py read sheets that contain abstracts, so they will not rerun
on these files. Rerunning stage0_search.py or fix_dois.py needs requests and
your own contact e-mail for the NCBI E-utilities (EMAIL near the top of each).

## Licence

Code (*.py): MIT. Data and text: CC BY 4.0. See LICENSE.
