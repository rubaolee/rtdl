# Call For Review - Goal5185 X-HD Exact-Oracle Subset8192 POD/OptiX

Please strictly review Goal5185.

## Files Under Review

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_larger_subset8192_optix_goal5185_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/goal5185_exact_oracle_subset8192_pod_optix_result_2026-07-08.md
```

Related prior evidence:

```text
history/internal_docs/goal5183_pod_optix_explicit_capacity_gate_result_2026-07-08.md
history/internal_docs/goal5184_larger_subset_pod_optix_scaling_result_2026-07-08.md
```

## Key Evidence

```text
source_limit=8192
backend=optix
native_symbol=rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
frontier_row_capacity=789009
row_capacity_policy=explicit
matched=true
route_abs_diff=0.0
frontier_rows=38249
total_candidate_distance_evaluations=6388308
exact_subset_pair_evaluations=4453597184
rtdl_route_wall_sec=1.4313380420207977
exact_subset_reference_sec=62.3426823168993
```

## Requested Checks

1. Does Goal5185 validly extend the exact-oracle POD/OptiX subset gate to 8192
   source rows?
2. Does the artifact prove `matched=true` and `route_abs_diff=0.0` against the
   exact subset oracle?
3. Is explicit capacity still safely above observed native frontier rows?
4. Does the report correctly identify exact-oracle validation cost as the next
   practical bottleneck?
5. Does the report avoid overclaiming all-source route completion, full paper
   reproduction, exact dataset identity, performance parity, or speedup ratio?
6. Is the suggested next decision appropriate: 16384 exact subset, route-only
   all-source smoke, or author `hd_exec` full-public comparator?

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
6. ...
```

Requested verdict label if approved:

```text
approve_goal5185_exact_oracle_subset8192__author_comparator_or_validation_mode_next
```
