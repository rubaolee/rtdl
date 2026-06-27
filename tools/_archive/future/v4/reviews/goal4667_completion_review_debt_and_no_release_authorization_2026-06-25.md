# Goal4667 Completion Review Debt And No Release Authorization

Date: 2026-06-25

Status: engineering complete, external review debt open

Goal:

`Goal4667 - Hausdorff adaptive CuPy argmax focused gate`

Engineering decision:

`hausdorff_focused_gate_passes_after_generic_adaptive_argmax__not_release_yet`

## Evidence To Review

- Report:
  `future/v4/v4_goal4667_hausdorff_adaptive_argmax_focused_gate_2026-06-25.md`
- Machine summary:
  `future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/summary.json`
- Raw POD evidence:
  `future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/`
- Code changes:
  - `src/rtdsl/partner_adapters.py`
  - `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
  - `tests/v4_goal4667_hausdorff_adaptive_argmax_test.py`

## External Review Debt

Claude review:

- status: open debt
- reason: Claude weekly-limit status is known; do not keep probing it.

Antigravity review:

- status: open debt
- reason: can review this packet asynchronously.

Third external seat:

- status: open debt
- reason: no available non-internal reviewer invoked synchronously.

## Non-Authorization

This record does not authorize:

- V4 release;
- formal high-performance V4;
- broad V4 speedup wording;
- whole-app speedup wording;
- public true-zero-copy wording;
- app-specific native Hausdorff kernels;
- arbitrary callback support;
- all-app rerun without Goal4668 protocol refresh.

## Review Questions

External reviewers should answer:

1. Is the optimization genuinely generic to
   `global_argmax_u32_f64_partner_columns`, rather than a Hausdorff-specific
   kernel?
2. Do the focused rows correctly compare against the frozen Goal4665 V3 CuPy
   denominator?
3. Do both focused rows clear correctness, V4/V3 hot `>=1.20x`, and prepare
   `>=0.80x`?
4. Is the 1M row correctly treated as a correctness-boundary probe, not a speed
   claim?
5. Is the non-authorization boundary strong enough to prevent jumping from this
   focused pass to public release wording?
