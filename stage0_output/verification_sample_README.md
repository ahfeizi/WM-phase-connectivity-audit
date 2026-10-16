# verification_sample.csv

Random full-text verification sample of 10 included records, drawn 2026-10-16.

- Population: the 101 included records in `coding_sheet_with_D12.csv` (after D19).
- Excluded from the frame (already checked at full text): R0261, R0101, R0434, R0580, R0256, R0506, R0225, R1004, R1005, R1008, R1011.
- Sampling frame: the remaining 90 rec_ids, sorted.
- Draw: `random.Random(20261016).sample(sorted_rec_ids, 10)` (Python 3.12.10).
- `draw_order` gives the order returned by `sample`; the other columns are the coding row as it stood at the draw.
