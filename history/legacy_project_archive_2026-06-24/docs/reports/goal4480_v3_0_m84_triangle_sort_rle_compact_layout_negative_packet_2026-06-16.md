# Goal4480 / V3.0 M84: Sort/RLE Compact Ray Layout Negative

## Verdict

Do not promote compact constant-ray columns for the current Triangle Counting route.

The candidate is correct, but it does not improve the M83 `numba_direct_sort_rle` path. Prepared ray-batch build gets a small 2-3% improvement, while total time is worse on all three large rows.

## Matrix

Warmup=1/repeat=3. Current means M83 full ray columns. Candidate means the same route with `--segment-ray-column-layout xz_constant_y_direction`.

| Dataset | Current total | Compact total | Compact speedup | Current batch build | Compact batch build | Batch speedup | Same count/rays/weights |
|---|---:|---:|---:|---:|---:|---:|---|
| com-lj | 6.489s | 7.025s | 0.924x | 0.695s | 0.681s | 1.020x | yes |
| soc-LiveJournal1 | 13.273s | 14.041s | 0.945x | 0.967s | 0.943s | 1.026x | yes |
| com-orkut | 35.990s | 36.510s | 0.986x | 6.124s | 5.953s | 1.029x | yes |

## Interpretation

M81 already showed the compact constant-ray ABI was correct but not a Triangle Counting route win. Goal4480 repeats the question after M83's sort/RLE improvement and gets the same route decision: full ray columns remain the current internal route.

The next useful work is not compact layout. It is further reducing sort/RLE unique-count cost, Numba key fill, or fused decode/projection.

## Artifacts

- `goal4480_v3_0_m84_triangle_sort_rle_compact_layout_com_lj_w1r3_2026-06-16.json`
- `goal4480_v3_0_m84_triangle_sort_rle_compact_layout_soc_livejournal1_w1r3_2026-06-16.json`
- `goal4480_v3_0_m84_triangle_sort_rle_compact_layout_com_orkut_w1r3_2026-06-16.json`
