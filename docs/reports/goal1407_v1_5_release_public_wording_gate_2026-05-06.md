# Goal 1407: v1.5 Release Docs And Public Wording Gate

Date: 2026-05-06

## Decision

The v1.5 release docs and public wording gate is closed as a release-candidate
gate.

This does not create a `v1.5` tag, move `v1.0`, authorize package-install
claims, or authorize whole-app speedup wording. It means the release-candidate
docs exist, are machine-checked for required boundary phrases, and avoid known
forbidden overclaims.

## Scope

The v1.5 release-candidate docs record:

- standalone Embree+OptiX language/runtime scope;
- 14 included app contracts;
- 4 excluded app rows;
- stable primitive names: `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`;
- `COLLECT_K_BOUNDED` remains experimental in v1.5;
- v1.5.1 is the collect-k promotion track;
- source-tree usage remains `PYTHONPATH=src:. python ...`;
- explicit release/tag action is still required.

## Implementation

Added `src/rtdsl/v1_5_release_public_wording.py` with:

- `v1_5_release_public_wording_gate()`
- `validate_v1_5_release_public_wording_gate()`

Added the v1.5 release-candidate package:

- `docs/release_reports/v1_5/README.md`
- `docs/release_reports/v1_5/release_statement.md`
- `docs/release_reports/v1_5/support_matrix.md`
- `docs/release_reports/v1_5/audit_report.md`
- `docs/release_reports/v1_5/tag_preparation.md`

Updated the front-page docs to point to the v1.5 release-candidate package while
preserving the current-release boundary.

## Release Gate Result

`same_contract_per_app_benchmarks` was already closed by Goal1406. With this
goal, `release_docs_and_public_wording` now passes too.

The aggregate v1.5 gate status is:

```text
release_candidate_ready_pending_explicit_release_action
```

The only next action is:

```text
request_explicit_v1_5_release_approval
```

## Verification

Command:

```sh
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1407_v1_5_release_public_wording_gate_test \
  tests.goal1398_v1_5_standalone_release_gate_test \
  tests.goal1406_v1_5_benchmark_evidence_matrix_test
```

Result: all tests passed.
