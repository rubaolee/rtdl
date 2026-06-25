# Antigravity Completion Review for `goal4628`

## Verdict: `accept_goal4628_second_gate_existing_pod_evidence`

As the independent AI completion reviewer, Antigravity has critically reviewed the second Tier-2 same-contract gate design and implementation under `goal4628`. We accept the gate using the existing RTX A5000 POD evidence. No fresh POD rerun is required before Goal4628 completion.

## Findings

1. **Fixed-Radius Wrapper Prerequisite**: Fully satisfied. The repository includes the public wrapper `src/rtdsl/v4_fixed_radius.py`, documentation, examples, and amendment closure (`claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md`). Tests verify the wrapper operates correctly.
2. **Gate Selection Validity**: Grouped-i64 is a valid second Tier-2 gate. It is non-fixed-radius and generic (`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`). This avoids using `weighted_sum` which remains candidate-only.
3. **Existing POD Evidence Sufficiency**: Fully sufficient. The existing RTX A5000 JSON evidence reports clean correctness parity passes across all 6 tested points (widths 1, 16, 256; rays 32K, 131K) and same-contract ratios > 1.0x.
4. **Honest Interpretation**: Same-contract comparisons and win sources are interpreted honestly. The speedup matches removing legacy host materialization.
5. **Width 256 Modest Ratio**: The 1.641x minimum is mechanically expected due to small group counts reducing legacy host materialization overhead. This does not require narrowing the claim or rerunning because all configurations exceed parity and the scorecard is strictly non-release.
6. **Preserved Boundaries**: The scorecard and packet strictly preserve all release, broad speedup, whole-app, true-zero-copy, Tier-3, CuPy, C ABI, and app-specific-kernel boundaries.

## Exit Gate Check: Pass

- Machine-checkable scorecard (`src/rtdsl/v4_second_gate_scorecard.py`) is verified.
- Regression test (`tests/v4_goal4628_second_gate_scorecard_test.py`) passes successfully.
- All focused prerequisite and regression tests (22 tests) ran and passed OK.
