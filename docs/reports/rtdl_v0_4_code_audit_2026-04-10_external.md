# RTDL v0.4 Code Audit (External Claude Report)

Date: 2026-04-10
Source report:
- `/Users/rl2025/claude-work/rtdl_v0_4_code_audit_2026-04-10.md`

## Status

External audit verdict: one real correctness issue found and fixed during the
audit-follow-up round.

This file preserves Claude's `v0.4` audit result produced from a separate local
clone. It is recorded here as external correctness evidence for the early
`fixed_radius_neighbors` line.

## What the external audit examined

- the `fixed_radius_neighbors` contract/documentation line through Goals 193-199
- DSL surface and lowering
- Python truth path
- native CPU/oracle path
- reference kernel and datasets
- existing Goal 198 / Goal 199 tests

## Main actionable finding

Claude identified one real medium-severity correctness gap in the pre-fix
state:

- `fixed_radius_neighbors` rows were not guaranteed to be grouped by ascending
  `query_id` in either:
  - the Python truth path
  - the native CPU/oracle path

That finding was adopted directly in this checkout and fixed at:

- [reference.py](/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py)
- [rtdl_oracle_api.cpp](/Users/rl2025/rtdl_python_only/src/native/oracle/rtdl_oracle_api.cpp)

Regression tests were added in:

- [goal198_fixed_radius_neighbors_truth_path_test.py](/Users/rl2025/rtdl_python_only/tests/goal198_fixed_radius_neighbors_truth_path_test.py)
- [goal199_fixed_radius_neighbors_cpu_oracle_test.py](/Users/rl2025/rtdl_python_only/tests/goal199_fixed_radius_neighbors_cpu_oracle_test.py)

That follow-up was committed on current main as:

- `9624dcd`

## Current-repo adoption notes

The external audit also contained broader notes and extra tests from Claude's
own review checkout. Those are preserved as external evidence, not copied into
this repo as if they were all authored here.

The deliberately adopted part is the concrete correctness fix and the matching
regression tests already present in the current checkout.

## External audit summary

The audit's most important conclusion was that the early `v0.4`
`fixed_radius_neighbors` line was structurally sound, but still needed one more
ordering fix before its contract could be considered truly closed. That
conclusion is now reflected directly in the repo history:

- [goal198_fixed_radius_neighbors_truth_path_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/goal198_fixed_radius_neighbors_truth_path_2026-04-10.md)
- [goal199_fixed_radius_neighbors_cpu_oracle_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/goal199_fixed_radius_neighbors_cpu_oracle_2026-04-10.md)
- [goal199_fixed_radius_neighbors_cpu_oracle_review_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/goal199_fixed_radius_neighbors_cpu_oracle_review_2026-04-10.md)
