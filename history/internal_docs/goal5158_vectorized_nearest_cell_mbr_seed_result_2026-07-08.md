# Goal5158 - Vectorized Nearest-Cell-MBR Seed Result

## Verdict

`completed_vectorized_generic_nearest_cell_mbr_seed`

## What Changed

Goal5158 optimizes the generic helper:

```text
seed_nearest_witness_from_nearest_cell_mbr_numpy_columns
```

The previous implementation had two Python-loop-shaped costs:

1. per-query selection of the nearest non-empty cell MBR;
2. per-query scanning of the selected seed cell's target points.

The new implementation keeps the same public helper and same app-neutral
contract, but replaces those internals with vectorized NumPy operations:

```text
query x cell MBR lower-bound matrix
-> ordered argmin over cells sorted by cell_id
-> expanded candidate query/target rows for selected seed cells
-> vectorized L2 distance
-> lexsort(query, distance, item_id)
-> nearest seed witness per query
```

Metadata now records:

```text
cell_mbr_selection = numpy_vectorized_ordered_argmin_min_distance_then_cell_id
seed_point_reduction_strategy = vectorized_expand_lexsort
contract = generic_seed_nearest_witness_from_nearest_cell_mbr
app_semantics = none
```

No X-HD-specific primitive, author symbol, paper name, or output semantics were
added to RTDL core.

## Files Changed

```text
src/rtdsl/partner_continuations.py
tests/goal5158_vectorized_nearest_cell_mbr_seed_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_seed_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Semantics Preserved

The seed remains an exact distance to one target point from one real target
cell, so it remains a valid upper bound for later frontier pruning. The helper
still:

- rejects empty query/target/cell inputs fail-closed;
- ignores empty cells for nearest-cell selection;
- validates cell point spans and target row indices;
- chooses minimum cell-MBR lower-bound distance;
- breaks equal cell-MBR lower-bound ties by lower `cell_id`;
- breaks equal exact point-distance ties by lower target `item_id`;
- reports no RT-core speedup or whole-app speedup claim.

The new regression test intentionally separates the two tie-break layers: it
uses a fixture where the selected lower `cell_id` contains a higher target id,
so a wrong implementation that lets exact target-id tie-break choose the cell
would fail.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_seed_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_seed_profile_pod.json
```

## Results

### sample256

```text
matched = true
author Running.AvgTime = 4.024 ms
RTDL route median = 0.018150337040424347 s
RTDL total median = 0.020074933767318726 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B seed = 0.0023451149463653564 s
A->B frontier = 0.0044570192694664 s
A->B nearest continuation = 0.0006110444664955139 s

B->A seed = 0.002279028296470642 s
B->A frontier = 0.002627149224281311 s
B->A nearest continuation = 0.0004963725805282593 s
```

### sample1024

```text
matched = true
author Running.AvgTime = 4.097 ms
RTDL route median = 0.11371012777090073 s
RTDL total median = 0.12062868475914001 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B seed = 0.020777471363544464 s
A->B frontier = 0.038665130734443665 s
A->B nearest continuation = 0.0058640167117118835 s

B->A seed = 0.02005431056022644 s
B->A frontier = 0.0120110884308815 s
B->A nearest continuation = 0.0039108917117118835 s
```

## Before / After Against Goal5157

The comparable Goal5157 production matrix reported:

```text
sample256 RTDL route median = 0.025988370180130005 s
sample1024 RTDL route median = 0.17047270387411118 s
```

Goal5158 reports:

```text
sample256 RTDL route median = 0.018150337040424347 s
sample1024 RTDL route median = 0.11371012777090073 s
```

So, for the RTDL route itself:

```text
sample256 route improvement ~= 1.43x vs Goal5157
sample1024 route improvement ~= 1.50x vs Goal5157
```

The targeted seed phase moved substantially:

```text
sample1024 seed median total before ~= 0.0959 s
sample1024 seed median total after  ~= 0.0408 s
seed phase improvement ~= 2.35x
```

The next measured route targets are now:

```text
sample1024 frontier median total     ~= 0.0507 s
sample1024 seed median total         ~= 0.0408 s
sample1024 continuation median total ~= 0.0098 s
```

## Interpretation

This is a real RTDL-route improvement for the current representative seeded
route, but it is **not** an author-performance parity claim.

The author and RTDL numbers still have different phase boundaries:

- author `Running.AvgTime` is the author's internal repeated algorithm timing;
- RTDL route median is an in-process Python/RTDL/partner route timing;
- exact paper datasets are still unavailable;
- this route is still not the author's fused X-HD RT-core implementation;
- no denominator-aligned author-vs-RTDL ratio is authorized.

The result is valuable because it removes the previous largest seed-side Python
loop from the representative route. After Goal5158, the largest measured phase
is native frontier row production, followed by the now-vectorized seed. The
next hard target is the generic/native frontier phase or a route design that
reduces frontier work.

## Validation

Local:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_seed_profile_pod.json
py -m unittest tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test
Ran 9 tests OK

py -m unittest tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5156_xhd_route_phase_median_profile_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test
Ran 15 tests OK
```

POD:

```text
python3 -m unittest tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test
Ran 12 tests OK (skipped=1)
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a generic RTDL/partner seed implementation improvement and
measured RTDL-route phase reduction on representative same-source fixtures.
