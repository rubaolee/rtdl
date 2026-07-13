# Goal5157 - Vectorized Frontier Nearest Continuation Result

## Verdict

`completed_vectorized_generic_frontier_nearest_continuation`

## What Changed

Goal5157 replaces the Python row-by-row implementation inside:

```text
nearest_witness_from_cell_mbr_frontier_numpy_columns
```

with an app-neutral NumPy vectorized continuation:

```text
frontier rows -> expanded candidate query/target arrays -> vectorized L2 distances
-> lexsort(query, distance, item_id) -> nearest witness per query
```

The helper remains generic:

```text
contract = generic_nearest_witness_from_cell_mbr_frontier
app_semantics = none
reduction_strategy = vectorized_expand_lexsort
```

It still consumes generic cell-MBR frontier rows and target cell point spans; no
X-HD-specific primitive, author symbol, paper name, or output semantics were
added to RTDL core.

## Files Changed

```text
src/rtdsl/partner_continuations.py
tests/goal5157_vectorized_frontier_nearest_continuation_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_continuation_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Correctness Semantics Preserved

The vectorized path preserves the previous semantics:

- pruned frontier rows are skipped;
- inline and offload frontier rows are consumed;
- invalid frontier kind codes still fail closed;
- span bounds are validated before expansion;
- seeded `current_best_distances/current_best_item_ids` remain valid candidates;
- nearest witness tie-break remains lower `item_id` for equal distance;
- missing query coverage still fails closed.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_continuation_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_continuation_profile_pod.json
```

## Results

### sample256

```text
matched = true
author Running.AvgTime = 4.028 ms
RTDL route median = 0.02598837018013 s
RTDL total median = 0.0280120074748993 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B seed = 0.00636035203933716 s
A->B frontier = 0.00449473410844803 s
A->B nearest continuation = 0.000619456171989441 s

B->A seed = 0.0062154158949852 s
B->A frontier = 0.00263595581054688 s
B->A nearest continuation = 0.00049155205488205 s
```

### sample1024

```text
matched = true
author Running.AvgTime = 4.508 ms
RTDL route median = 0.170472703874111 s
RTDL total median = 0.179116323590279 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B seed = 0.0488816201686859 s
A->B frontier = 0.0402925163507462 s
A->B nearest continuation = 0.00642359256744385 s

B->A seed = 0.0470491871237755 s
B->A frontier = 0.0119445100426674 s
B->A nearest continuation = 0.0038575604557991 s
```

## Before / After Against Goal5156

The comparable Goal5156 production median profile was:

```text
sample256 RTDL route median = 0.0379673168063164 s
sample1024 RTDL route median = 0.288512669503689 s
```

Goal5157 reports:

```text
sample256 RTDL route median = 0.02598837018013 s
sample1024 RTDL route median = 0.170472703874111 s
```

So, for the RTDL route itself:

```text
sample256 route improvement ~= 1.46x vs Goal5156
sample1024 route improvement ~= 1.69x vs Goal5156
```

The largest intended phase moved substantially:

```text
sample1024 continuation median total before ~= 0.1354 s
sample1024 continuation median total after  ~= 0.0103 s
```

The next measured route targets are now:

```text
sample1024 seed median total     ~= 0.0959 s
sample1024 frontier median total ~= 0.0522 s
sample1024 continuation total    ~= 0.0103 s
```

## Interpretation

This is a real RTDL-route improvement for the current representative seeded
route, but it is **not** an author-performance parity claim.

The author number and RTDL number still have different phase boundaries:

- author `Running.AvgTime` is the author's internal repeated algorithm timing;
- RTDL route median is an in-process Python/RTDL/partner route timing;
- no exact paper dataset is involved;
- no full paper reproduction is claimed.

The result is valuable because it removes the previous largest Python loop from
the representative route and shows the next bottleneck: nearest-cell-MBR seed
selection, followed by native frontier rows.

## Validation

Local:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_continuation_profile_pod.json
py -m unittest tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5156_xhd_route_phase_median_profile_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test
Ran 12 tests OK
```

POD:

```text
python3 -m unittest tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test
Ran 6 tests OK
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused continuation inside OptiX;
- whole-program performance reproduction.

It claims only a generic RTDL/partner continuation implementation improvement
and measured route-phase reduction on representative same-source fixtures.
