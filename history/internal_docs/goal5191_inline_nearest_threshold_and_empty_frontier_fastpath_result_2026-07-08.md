# Goal5191 - Inline Nearest Threshold And Empty-Frontier Fast Path Result

## Status

`implemented_review_pending`

## Objective

After Goal5189, the fastest full-public Level-B X-HD route used the generic
local-grid seed. It reduced seed time but increased frontier and continuation
work:

```text
Goal5189 local-grid route ~= 5.98s
frontier rows           = 7,590,188
nearest continuation    ~= 2.03s
```

Goal5191 tests whether the existing generic native inline-nearest payload can
consume more cell-MBR frontier work inside the native collector by increasing
`max_inline_points`, and then removes an app-runner orchestration overhead when
the inline state fully resolves every query and the frontier row table is empty.

This is a generic route-internal X-HD Level-B improvement. It is not exact paper
dataset reproduction, not full paper reproduction, and not an author-vs-RTDL
performance ratio.

## Implementation

### Runner Empty-Frontier Fast Path

Changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5191_inline_frontier_fastpath_test.py
```

The route runner now uses `_nearest_from_complete_frontier_state(...)` when:

```text
frontier["metadata"]["row_count"] == 0
```

The helper converts the native `nearest_state` into generic nearest columns only
when all of the following hold:

- source ids exactly match `nearest_state["query_point_ids"]`;
- nearest item ids are all non-negative;
- nearest distances are all finite.

Otherwise it fails closed with `RuntimeError`.

The produced metadata is app-neutral:

```text
contract = generic_nearest_witness_from_complete_frontier_state
app_semantics = none
executor = complete_frontier_state_passthrough
candidate_distance_evaluations = 0
```

The full-public summary now records:

```text
max_inline_points
complete_frontier_state_passthrough
```

inside each `rtdl_route` block so the result can be audited without relying on
the file name.

## Validation

### Local Tests

```text
py -m unittest \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5190_grid_branch_bound_seed_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 17 tests in 1.488s
OK
```

The local `py` command printed the known environment noise:

```text
Could not find platform independent libraries <prefix>
```

### POD Tests

POD preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD unit tests:

```text
python3 -m unittest \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5190_grid_branch_bound_seed_test

Ran 13 tests in 0.535s
OK
```

### Full-Public Level-B Route

Final artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_full_public_all_source_local_grid_seed_inline512_fastpath_goal5191_final_graphics_dragon_happy_buddha_2026-07-08.json
```

Command regime:

```text
backend = optix
grid_shape = 32,32,32
source_limits = all
initial_state = local-grid-cell
frontier_inline_nearest = true
max_inline_points = 512
frontier_row_order = native
frontier_row_capacity = 4,000,000
skip_exact_oracle = true
author_hd_result = 0.12572988867759705
author_tolerance = 1e-6
```

Final result:

```text
matched = true
rtdl_route_distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
route_wall = 3.647909864783287s
total = 6.382600784301758s
frontier_rows = 0
max_inline_points = 512
complete_frontier_state_passthrough = true
nearest_executor = complete_frontier_state_passthrough
total_candidate_distance_evaluations = 23,668,840
continuation_candidate_distance_evaluations = 0
```

Phase timings:

```text
initial_state_seed = 0.8847416788339615s
frontier_rows = 2.0016997531056404s
nearest_continuation = 0.016401365399360657s
max_nearest_reduction = 0.07365364581346512s
```

## Threshold Sweep

All runs used the same full public Stanford Dragon/HappyBuddha Level-B pair,
`backend=optix`, `initial_state=local-grid-cell`, native frontier order,
inline-nearest enabled, and author-only comparison against the Goal5186 author
HDResult.

| Route | max_inline_points | matched | frontier rows | route wall | continuation | total evals |
|---|---:|---:|---:|---:|---:|---:|
| Goal5189 local-grid baseline | 64 | true | 7,590,188 | 5.982s | 2.031s | 1,109,149,179 |
| Goal5191 inline128 | 128 | true | 3,647,552 | 4.970s | 1.147s | 744,934,163 |
| Goal5191 inline256 | 256 | true | 505,884 | 4.027s | 0.337s | 184,811,823 |
| Goal5191 inline512 | 512 | true | 0 | 3.723s | 0.155s | 23,668,840 |
| Goal5191 inline512 + fast path | 512 | true | 0 | 3.648s | 0.016s | 23,668,840 |

The route wall improvement from the empty-frontier fast path is modest because
seed/frontier native work dominates after `max_inline_points=512`. The phase
improvement is clear: the empty continuation call drops from about `0.155s` to
about `0.016s`.

## Interpretation

Goal5191 shows that, for this full-public Level-B route, increasing the generic
native inline-nearest threshold is a better next move than the Goal5190
grid-branch-bound seed. At `max_inline_points=512`, the native inline payload
resolves every query, so there are no frontier rows left for continuation.

The remaining route floor is now dominated by:

```text
native frontier / inline-nearest collector ~= 2.00s
local-grid seed ~= 0.88s
```

The project should not keep attacking Python continuation for this route while
`frontier_row_count=0`. The next route-internal work, if any, must target the
generic native inline-nearest collector or the local-grid seed cost.

## Claim Boundary

Authorized:

- Level-B same-source full-public Dragon/HappyBuddha route improvement.
- Generic inline-nearest threshold evidence.
- Empty-frontier runner fast path evidence.
- Correctness against the Goal5186 author HDResult for the public
  Dragon/HappyBuddha candidate.

Not authorized:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- Figure 5-11 reproduction;
- claim that `max_inline_points=512` is globally optimal;
- claim that this is the author's fused X-HD RT-core algorithm.

## Next Work

If continuing route performance, choose one of:

1. profile and optimize the generic native 3-D inline-nearest collector;
2. reduce local-grid seed cost further without increasing frontier work;
3. stop route micro-optimization and move back to review/provenance because
   the current Level-B route already matches author HDResult and the next costs
   are deeper native/algorithmic work.
