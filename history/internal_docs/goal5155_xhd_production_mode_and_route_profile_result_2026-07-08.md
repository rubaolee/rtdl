# Goal5155 - X-HD Production Mode And Route Profile Result

## Verdict

`completed_production_author_only_matrix_and_seeded_route_profile`

## What Changed

Goal5155 separates the RTDL X-HD route into two explicitly labeled validation
regimes:

```text
exact-and-author  -> runs exact reference plus optional author HDResult check
author-only       -> skips exact reference; compares only to author HDResult
none              -> skips exact and author checks; route/profile only
```

The default remains `exact-and-author`, so existing correctness gates keep their
strong validation behavior. The new `author-only` mode is for production-style
timing where exact-reference validation is not part of the user route.

Goal5155 also adds per-direction subphase timing inside the seeded cell-MBR
frontier route:

```text
source_columns
target_columns
grid_cell_mbrs
initial_state_seed
radius_selection
frontier_rows
nearest_continuation
max_nearest_reduction
direction_total
```

## Files Changed

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
tests/goal5155_xhd_production_validation_and_route_profile_test.py
```

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_matrix_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_matrix_pod.json
```

## Results

### sample256

Correctness / validation:

```text
validation_mode = author-only
matched = true
author HDResult = 0.11612465232610703
RTDL directed A->B = 0.11612464969699586
author_abs_diff = 2.6291111648868437e-09
exact_reference_sec_median = null
rtdl_matches_exact_reference = null
```

Timing:

```text
author Running.AvgTime = 4.038 ms
author process wall = 1.11088158935308 s
RTDL route median = 0.0387897193431854 s
RTDL load median = 0.00164520740509033 s
RTDL total median = 0.0407581254839897 s
```

Last-run route profile:

```text
A->B seed = 0.00653677433729172 s
A->B frontier = 0.00447268038988113 s
A->B nearest continuation = 0.00828001648187637 s
B->A seed = 0.00629393011331558 s
B->A frontier = 0.00355099141597748 s
B->A nearest continuation = 0.00501270592212677 s
```

### sample1024

Correctness / validation:

```text
validation_mode = author-only
matched = true
author HDResult = 0.1215052381157875
RTDL directed A->B = 0.12150523439597159
author_abs_diff = 3.7198159136275777e-09
exact_reference_sec_median = null
rtdl_matches_exact_reference = null
```

Timing:

```text
author Running.AvgTime = 4.068 ms
author process wall = 1.04177387058735 s
RTDL route median = 0.301321744918823 s
RTDL load median = 0.00605670362710953 s
RTDL total median = 0.308213144540787 s
```

Last-run route profile:

```text
A->B seed = 0.0493946671485901 s
A->B frontier = 0.0396153330802917 s
A->B nearest continuation = 0.0817508772015572 s
B->A seed = 0.0477351620793343 s
B->A frontier = 0.0116917192935944 s
B->A nearest continuation = 0.0564307048916817 s
```

## Interpretation

Goal5155 does **not** make the RTDL route faster by changing the algorithm. It
makes the timing boundary honest:

- Goal5154 measured `exact-and-author`, so RTDL `total_sec` included exact
  validation. On sample1024 that exact-reference median was about `1.665s`.
- Goal5155 measures `author-only`, so production-style `total_sec` excludes that
  exact-reference validation and falls to about `0.308s` for sample1024.

This is a measurement-boundary correction and profiling improvement, not a new
performance-parity claim.

The profile shows the current seeded route is dominated by:

```text
nearest_continuation + nearest-cell-MBR seed + native frontier rows
```

For sample1024, the last-run A->B direction spends roughly:

```text
nearest_continuation ~0.082s
seed                 ~0.049s
frontier_rows        ~0.040s
```

So the next real performance target is to move more of the seed/continuation
work out of Python/NumPy partner code, or to explicitly accept that the current
route is a correctness-preserving representative route rather than author
`Running.AvgTime` parity.

## Validation

Local:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_matrix_pod.json
py -m unittest tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test
Ran 10 tests OK
```

POD:

```text
python3 -m unittest tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test
Ran 6 tests OK
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- speedup;
- denominator-aligned author-vs-RTDL ratio;
- that author-only validation is as strong as exact-reference validation.

It provides a production-style timing boundary and subphase route profile for
the current representative seeded RTDL route.
