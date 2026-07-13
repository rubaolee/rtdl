# Goal5211 Global-Bound Early-Break Result

Date: 2026-07-09

## Verdict

```text
completed_global_bound_early_break_win__explicit_max_nearest_contract_pending_review
```

## Purpose

After Goals5208-5210, the remaining X-HD Level-B warm route floor was native
inline-nearest traversal, not Python continuation, row materialization, static
cell ordering, trace flags, or accel-build setup.

Author X-HD uses traversal-local state plus a global directed-Hausdorff bound:

```text
cmax2 = global best known max-nearest distance
cmin2 = current query nearest distance
if a query finds a candidate <= cmax2, it cannot increase directed HD and can abort
completed exact queries can raise cmax2
```

Goal5211 tests the same idea as a generic RTDL contract:

```text
generic max-nearest / directed-Hausdorff global-bound early break
```

This is not an X-HD-specific primitive. It is valid only for reductions where
the final answer is the maximum over per-source nearest distances. For
early-aborted sources, the per-source witness may be approximate; the final
directed-HD distance remains correctness-gated against the author value.

## Implementation

Changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5211_global_bound_early_break_contract_test.py
AGENTS.md
memory/progress.md
memory/decisions.md
memory/todo.md
```

Native ABI:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5
```

The old v1-v4 native symbols remain compatibility-preserving. Existing callers
keep global-bound early break disabled.

New optional public argument:

```text
global_bound_early_break: bool = False
```

Contract metadata includes:

```text
global_bound_early_break
global_bound_early_break_count
global_bound_distance
global_bound_contract = generic_max_nearest_global_bound_early_break
per_source_witness_exact
inline_nearest_contract =
  native_inline_cell_point_nearest_with_global_bound_early_break_for_max_nearest_reductions
```

## Validation

Local:

```text
py -m unittest \
  tests.goal5211_global_bound_early_break_contract_test \
  tests.goal5210_cell_mbr_disable_closesthit_flag_test \
  tests.goal5209_cell_order_work_ordering_test

Ran 8 tests OK

py -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/partner_continuations.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  tests/goal5211_global_bound_early_break_contract_test.py

OK

git diff --check
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python -m unittest \
  tests.goal5211_global_bound_early_break_contract_test \
  tests.goal5210_cell_mbr_disable_closesthit_flag_test

Ran 5 tests OK

make build-optix
OK
```

## POD Evidence

Workload:

```text
Level-B same-source public Stanford Dragon -> HappyBuddha
source_limits = all
grid_shape = 32,32,32
initial_state = local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
frontier_row_order = native
cell_order = native
global_bound_early_break = true
collect_frontier_native_phase_timings = true
author comparator = Goal5186 HDResult
```

Fresh no-warm artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_fresh_graphics_dragon_happy_buddha_2026-07-09.json
```

Warm protocol artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_repeat1_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_repeat2_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_repeat3_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

All runs:

```text
matched = true
author_abs_diff ~= 2.38e-9
frontier_rows = 0
native symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5
global_bound_early_break = true
per_source_witness_exact = false
```

## Performance

Fresh no-warm:

| route | route wall | case total | full total incl load | frontier phase | native total | OptiX launch | early breaks |
|---|---:|---:|---:|---:|---:|---:|---:|
| Goal5211 global-bound | 0.849s | 1.065s | 1.752s | 0.423s | 0.268s | 0.041s | 409,198 |

Warm protocol measured repeats:

| artifact | route wall | case total | frontier phase | native total | OptiX launch | early breaks |
|---|---:|---:|---:|---:|---:|---:|
| first | 0.284s | 0.466s | 0.071s | 0.062s | 0.041s | 409,191 |
| repeat1 | 0.421s | 0.600s | 0.085s | 0.077s | 0.066s | 410,637 |
| repeat2 | 0.308s | 0.486s | 0.068s | 0.058s | 0.037s | 409,256 |
| repeat3 | 0.416s | 0.597s | 0.090s | 0.083s | 0.066s | 409,954 |
| median | 0.362s | 0.541s | 0.078s | 0.069s | 0.053s | 409,605 |

Comparison to recent baselines:

| regime | previous route | Goal5211 route | interpretation |
|---|---:|---:|---|
| fresh no-warm | Goal5205 route ~=1.16-1.17s | 0.849s | real fresh route improvement |
| full total incl load | Goal5205 total ~=2.06s | 1.752s | real user-visible improvement under same Level-B route |
| explicit warm measured | Goal5210 median ~=0.612s | 0.362s | substantial warm route improvement |
| OptiX launch / inline scan | Goal5210 median ~=0.372s | 0.053s | global bound removes most native inline scan work |

## Interpretation

This is the first post-Goal5205 route change that materially attacks the native
inline-nearest floor. It works because it changes the execution model rather
than retuning thresholds or row ordering:

```text
old route: each source query computes a full exact nearest witness independently
new route: once global max-nearest bound is known, many source queries can abort
           after finding any candidate below that bound
```

About 409k of 437,645 source queries early-abort on this workload.

## Claim Boundary

Allowed:

```text
Goal5211 adds an optional generic max-nearest global-bound early-break contract.
On the Level-B Dragon/HappyBuddha public route it preserves author HDResult and
improves route-local performance.
```

Not authorized:

```text
full X-HD paper reproduction
exact paper dataset identity
author-vs-RTDL performance ratio
X-HD-specific RTDL primitive
exact per-source nearest witness for early-aborted sources
using warm numbers as fresh headline
default enablement for generic nearest-witness APIs
```

## Next Recommendation

Send Goal5211 for strict review before making it a default route. If approved,
the X-HD Level-B performance route can use this flag because the app consumes
the directed-HD distance, not exact per-source witness identity. Generic
nearest-witness APIs should keep it explicit because early-aborted per-source
witnesses may be approximate.
