# Call For Review - Goal5183 X-HD POD/OptiX Explicit Capacity Gate

Please strictly review Goal5183.

## Files Under Review

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
src/rtdsl/partner_continuations.py
tests/goal5182_xhd_explicit_frontier_capacity_test.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_explicit_capacity_optix_goal5183_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/goal5183_pod_optix_explicit_capacity_gate_result_2026-07-08.md
```

Related prior evidence:

```text
history/internal_docs/goal5179_priority_input_scale_profile_result_2026-07-08.md
history/internal_docs/goal5180_full_public_candidate_feasibility_gate_result_2026-07-08.md
history/internal_docs/goal5181_full_public_subset_scaling_gate_result_2026-07-08.md
history/internal_docs/goal5182_explicit_frontier_capacity_readiness_result_2026-07-08.md
```

## Context

Goal5181 observed max local frontier rows of `526006` for source limits
16/64/128 against the full public HappyBuddha target and suggested explicit
capacity:

```text
789009 = ceil(526006 * 1.5)
```

Goal5182 threaded that explicit capacity through the route runner and proved
local fail-closed semantics.

Goal5183 runs the same bounded gate on a CUDA/OptiX POD.

## Key Evidence

POD:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Artifact summary:

```text
goal: Goal5183
backend: optix
all_matched: true
max_frontier_row_count: 528
median_route_wall_sec: 0.6765436306595802
```

Per case:

```text
source_limit=16:  matched=true, route_abs_diff=0.0, rows=69,  capacity=789009, policy=explicit
source_limit=64:  matched=true, route_abs_diff=0.0, rows=294, capacity=789009, policy=explicit
source_limit=128: matched=true, route_abs_diff=0.0, rows=528, capacity=789009, policy=explicit
```

Native metadata:

```text
frontier_native_symbol: rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
frontier_row_order: native_unsorted
frontier_inline_nearest: true
```

## Requested Checks

1. Does Goal5183 truly exercise the POD/OptiX native frontier path, as shown by
   backend `optix` and native symbol
   `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3`?
2. Does every source limit match the exact subset oracle with
   `route_abs_diff=0.0`?
3. Is explicit capacity `789009` carried to the native path and recorded with
   `row_capacity_policy=explicit`?
4. Is the small native frontier row count (`528` max) correctly explained by
   `inline_nearest=true` rather than by hidden truncation?
5. Does the report avoid claiming all-source completion, full paper
   reproduction, exact dataset identity, figure reproduction, or performance
   ratio?
6. Is the cross-platform path normalization fix appropriate for consuming
   Windows-authored bridge artifacts on Linux/POD?
7. Does the next step correctly move to larger bounded source subsets before
   any all-source claim?
8. Are there any missing metadata fields or claim-boundary issues that should
   block Goal5183 closeout?

## Expected Answer Shape

Please answer with:

```text
Verdict: <approve / approve_with_required_amendments / block>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to requested checks:
1. ...
2. ...
...
8. ...
```

Requested verdict label if approved:

```text
approve_goal5183_pod_optix_explicit_capacity_bounded_gate__larger_subset_next
```
