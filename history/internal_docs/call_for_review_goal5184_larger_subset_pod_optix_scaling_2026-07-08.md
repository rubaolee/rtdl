# Call For Review - Goal5184 X-HD Larger Bounded POD/OptiX Subset Scaling

Please strictly review Goal5184.

## Files Under Review

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset1024_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset2048_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset4096_optix_goal5184_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/goal5184_larger_subset_pod_optix_scaling_result_2026-07-08.md
```

Relevant implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
src/rtdsl/partner_continuations.py
```

## Context

Goal5183 validated source limits 16/64/128 on POD/OptiX with explicit frontier
capacity `789009`.

Goal5184 increases the bounded source subset to:

```text
256, 512, 1024, 2048, 4096
```

against the same full public HappyBuddha target (`543652` points).

## Key Evidence

All cases:

```text
backend=optix
native_symbol=rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
frontier_row_capacity=789009
row_capacity_policy=explicit
frontier_inline_nearest=true
frontier_row_order=native_unsorted
matched=true
route_abs_diff=0.0
```

Summary:

```text
source_limit=256:  frontier_rows=1221,  candidate_evals=202495
source_limit=512:  frontier_rows=2426,  candidate_evals=403005
source_limit=1024: frontier_rows=4516,  candidate_evals=750202
source_limit=2048: frontier_rows=9691,  candidate_evals=1617780
source_limit=4096: frontier_rows=19229, candidate_evals=3203273
```

## Requested Checks

1. Does Goal5184 correctly extend the POD/OptiX bounded gate beyond Goal5183
   while keeping exact subset oracle validation?
2. Do all cases match with `route_abs_diff=0.0`?
3. Is explicit capacity still safely above observed native frontier rows?
4. Is the interpretation of small native frontier row counts under
   `inline_nearest=true` correct and not evidence of truncation?
5. Does the report avoid converting bounded subset evidence into an all-source,
   full-paper, figure, exact-dataset, performance-ratio, or author-parity
   claim?
6. Are the route wall timings correctly treated as noisy bounded-run timings,
   not as a paper performance matrix?
7. Is Goal5185's proposed next decision point appropriate: larger exact subset
   vs route-only/all-source smoke vs author `hd_exec` full-public comparator?
8. What amendments, if any, are required before closing Goal5184?

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
approve_goal5184_larger_bounded_pod_optix_subset_scaling__validation_boundary_next
```
