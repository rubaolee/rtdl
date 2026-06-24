# Goal4479 / V3.0 M83: Triangle Sort/RLE Unique-Count Candidate

## Verdict

M83 is a real internal optimization. It keeps the same Triangle Counting route shape as M78/M82, but replaces the hottest Goal4478 step, `cp.unique(return_counts)`, with explicit in-place CuPy sort plus run-length counting after the Numba direct key fill.

This is still a Python/partner implementation. It does not add C++/CUDA native engine customization, does not change the RTDL primitive contract, and does not authorize public speedup wording.

## Route Compared

Baseline:

- `unique_weighted`
- `numba_direct`
- `prepared_segment_replay`
- full ray columns

Candidate:

- `unique_weighted`
- `numba_direct_sort_rle`
- `prepared_segment_replay`
- full ray columns

The only intended difference is the unique/count step over duplicate two-hop keys.

## Performance Matrix

These rows are warmup=1/repeat=3, without synchronized phase telemetry.

| Dataset | Count | Baseline total | M83 total | Total speedup | Baseline segment build | M83 segment build | Segment-build speedup | Query speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| com-lj | 177,820,130 | 7.308s | 6.489s | 1.126x | 1.316s | 1.149s | 1.145x | 0.999x |
| soc-LiveJournal1 | 285,730,264 | 14.467s | 13.273s | 1.090x | 1.719s | 1.496s | 1.149x | 1.005x |
| com-orkut | 627,584,181 | 38.564s | 35.990s | 1.071x | 8.646s | 7.281s | 1.187x | 0.998x |

All three rows preserve the same triangle count, lowered ray count, and lowered ray weight sum as the `numba_direct` baseline.

## Phase Check

The synchronized telemetry rows confirm the candidate takes the intended path: the old `cupy_unique_counts` phase is replaced by `cupy_sort_rle_counts`.

| Dataset | Telemetry segment build | `cupy_sort_rle_counts` |
|---|---:|---:|
| com-lj | 1.557s | 0.596s |
| soc-LiveJournal1 | 2.153s | 0.890s |
| com-orkut | 10.970s | 5.458s |

The improvement is meaningful, but the unique/count boundary is still the largest segment-ray construction cost on large rows. M83 should be promoted as the current internal route, not treated as the end of the Triangle Counting optimization line.

## Route Decision

Promote `--segment-unique-key-builder numba_direct_sort_rle` as the current internal Triangle Counting route for the prepared segmented RT-2A1 path.

Keep the boundaries:

- no public speedup claim;
- no broad Triangle Counting RT-core acceleration claim;
- no automatic partner selection;
- no native app-specific engine logic;
- no claim that partner materialization is solved.

## Artifacts

- `goal4479_v3_0_m83_triangle_sort_rle_candidate_com_lj_numba_direct_w1r3_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_com_lj_numba_direct_sort_rle_w1r3_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_com_lj_numba_direct_sort_rle_w1r1_telemetry_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_soc_livejournal1_numba_direct_w1r3_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_soc_livejournal1_numba_direct_sort_rle_w1r3_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_soc_livejournal1_numba_direct_sort_rle_w1r1_telemetry_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_com_orkut_numba_direct_w1r3_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_com_orkut_numba_direct_sort_rle_w1r3_2026-06-16.json`
- `goal4479_v3_0_m83_triangle_sort_rle_candidate_com_orkut_numba_direct_sort_rle_w1r1_telemetry_2026-06-16.json`
