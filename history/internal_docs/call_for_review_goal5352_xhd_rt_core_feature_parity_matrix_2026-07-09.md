# Call For Review - Goal5352 X-HD RT-Core Feature Parity Matrix

Please strictly review Goal5352.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5352_rt_core_parity_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5352_rt_core_feature_parity_matrix.json
tests/goal5352_xhd_rt_core_feature_parity_matrix_test.py
history/internal_docs/goal5352_xhd_rt_core_feature_parity_matrix_result_2026-07-09.md
```

Useful supporting artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5351_author_variant_semantics_audit.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5350_functional_parity_matrix_amendment.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5282_author_offload_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

## Review Questions

1. Does Goal5352 correctly interpret Goal5351: accepting `eb/nn/itk/clover/rt`
   names is value-surface compatibility, not author algorithm parity?

2. Does the matrix correctly keep
   `author_rt_core_algorithm_parity_ready=false` and
   `full_xhd_paper_reproduction_ready=false`?

3. Does the current wrapper-surface audit correctly show that author RT options
   such as `fast_build_bvh`, `rebuild_bvh`, `eb`, `prune`, `lb`,
   `n_points_cell`, `tune_grid`, and `tune_radius` are not yet exposed by
   `run_xhd_rtdl_hd_exec.py`, while `Radius` is kept as an iteration/internal
   field rather than a CLI option?

4. Are the listed feature gaps the right ones for same-functionality with the
   author `rt` implementation: RT option surface, grid/cell-MBR structure,
   radius growth / tune-radius, early-break/prune scalar contract,
   load-balance/heavy offload, Figure 11 memory fields, Figure 5 baselines,
   and exact paper input identity?

5. Does the artifact avoid overclaiming? In particular, does it avoid claiming
   author RT-core algorithm identity, Figure 5/7/8/9/11 reproduction, full
   paper reproduction, and performance ratio?

6. Is `author_rt_option_surface_gate` the right next implementation target, or
   should the next target instead be radius-growth / tune-radius semantics or
   load-balance / heavy-offload denominator alignment?

7. Are the tests strong enough to prevent accidental upgrade from "partial /
   not reproduced" to "closed" without evidence?

8. Does this goal preserve the RTDL principle that core exposes generic spatial
   primitives and the X-HD app owns paper-specific flags, wrappers, comparators,
   and claim boundaries?

9. Is there any stale or contradictory evidence in the supporting artifacts
   that should change the matrix?

10. Should Goal5352 close with:

```text
rt_core_feature_parity_matrix_ready__next_target_author_rt_option_surface
```

## Expected Answer Shape

Please answer with:

```text
Verdict:
  approve | approve_with_required_amendments | block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  ...

Recommended next target:
  ...
```

Possible verdict labels:

```text
approve_goal5352_rt_core_feature_parity_matrix
revise_goal5352_rt_core_feature_parity_matrix
block_goal5352_rt_core_feature_parity_matrix
```
