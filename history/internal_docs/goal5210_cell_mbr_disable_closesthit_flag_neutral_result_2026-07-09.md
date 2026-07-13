# Goal5210 Cell-MBR Disable-Closest-Hit Flag Neutral Result

Date: 2026-07-09

## Verdict

```text
completed_cell_mbr_disable_closesthit_semantic_cleanup__no_material_speedup
```

## Purpose

After Goal5208 and Goal5209, the current X-HD Level-B warm route still has a
steady native inline-nearest floor:

```text
measured warm route ~= 0.626s
native OptiX launch / inline scan ~= 0.37s
frontier rows = 0
```

Goal5210 tested a small generic OptiX execution-model cleanup: the generic
cell-MBR frontier pipeline has raygen, miss, intersection, and any-hit programs,
but no closest-hit program. The ray trace previously used:

```text
OPTIX_RAY_FLAG_NONE
```

This goal changes only the generic cell-MBR frontier raygen trace to:

```text
OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT
```

This is not an X-HD-specific primitive and does not change app semantics.

## Implementation

Changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
tests/goal5210_cell_mbr_disable_closesthit_flag_test.py
```

The change is scoped to:

```text
__raygen__cell_mbr_frontier3d
```

Other OptiX workloads in the same native source keep their previous trace flags.

## Validation

Local:

```text
py -m unittest \
  tests.goal5210_cell_mbr_disable_closesthit_flag_test \
  tests.goal5209_cell_order_work_ordering_test \
  tests.goal5207_explicit_route_warmup_protocol_test

Ran 7 tests OK

py -m py_compile tests/goal5210_cell_mbr_disable_closesthit_flag_test.py
OK

git diff --check -- src/native/optix/rtdl_optix_workloads.cpp \
  tests/goal5210_cell_mbr_disable_closesthit_flag_test.py
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python -m unittest tests.goal5210_cell_mbr_disable_closesthit_flag_test
Ran 2 tests OK

make build-optix
OK
```

## POD Evidence

Same full-public Stanford Dragon -> HappyBuddha Level-B workload and same
Goal5207 explicit warmup protocol:

```text
source_limits = all
route_warmup_source_limit = all
max_inline_points = 512
cell_order = native
frontier_inline_nearest = true
collect_frontier_native_phase_timings = true
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5210_disable_closesthit_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5210_disable_closesthit_repeat1_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5210_disable_closesthit_repeat2_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5210_disable_closesthit_repeat3_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

All runs:

```text
matched = true
frontier_rows = 0
```

## Same-POD Repeat Comparison

Baseline is Goal5209 native cell order repeats, before the trace-flag change.

| route | route median | route min | route max | case median | native median | OptiX launch median |
|---|---:|---:|---:|---:|---:|---:|
| Goal5209 native baseline | 0.615933s | 0.601413s | 0.616578s | 0.797471s | 0.393540s | 0.371376s |
| Goal5210 disable closest-hit | 0.611615s | 0.597219s | 0.614034s | 0.793001s | 0.393301s | 0.371655s |

The route median moves by about:

```text
0.0043s
```

But the native OptiX launch median does not improve:

```text
0.371376s -> 0.371655s
```

The small route movement is therefore noise / neighboring phase movement, not a
credible native execution-model win.

## Interpretation

The flag is semantically appropriate for this generic pipeline because no
closest-hit program is used. However, on the current Level-B route it does not
materially move the native inline-nearest floor.

Keep the code change as a scoped semantic cleanup, but do not claim:

- route speedup;
- author parity;
- full paper reproduction;
- a new X-HD-specific primitive;
- that the remaining native inline-nearest floor has been solved.

## Claim Boundary

This goal claims:

- the generic cell-MBR frontier raygen now disables closest-hit traversal;
- correctness is preserved on the full-public Level-B route;
- the change is neutral / noise-level for performance.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- a meaningful route optimization;
- a warm-only headline.

## Next

Do not spend more goals on trace-flag micro-tuning without new evidence.

The next meaningful route attack still has to change the native inline-nearest
execution model or introduce a stronger generic prepared/runtime spatial
strategy.
