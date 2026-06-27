# V4 `goal4621` Completion Consensus And Review Debt

Date: 2026-06-24
Author: Codex
Status: `goal4621_complete_not_release`

## Verdict

`goal4621` is complete:

- catalog/front-door hardening is implemented
- local tests pass
- POD GPU catalog gate passes
- release remains unauthorized
- measured-catalog promotion remains unauthorized

This record closes `goal4621` bookkeeping and authorizes proceeding to
`goal4622`. It does not authorize V4 release, public speedup wording, measured
promotion, or public true-zero-copy wording.

## Consensus Seats

### Seat 1: Codex Implementation And Self-Audit

Codex implemented `goal4621` as catalog/front-door hardening only.

Changed scope:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_fixed_radius.py`
- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4_point_group.py`
- `scripts/v4_catalog_regression_gate.py`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_ray_triangle_device_array_api_test.py`

Completion packet:

- `future/v4/reviews/call_for_review_v4_goal4621_catalog_hardening_completion_2026-06-24.md`

### Seat 2: Claude

Review file:

- `future/v4/reviews/claude_v4_goal4621_catalog_hardening_completion_review_2026-06-24.raw.md`

Verdict:

- `accept_goal4621_complete_not_release`

Claude verified:

- all catalog rows expose the hardened status/claim fields
- measured and candidate rows are cleanly separated
- the weighted-sum candidate remains unpromoted
- `claim_boundary_v4()` reports five measured surfaces and one candidate
- the public true-zero-copy sanitizer is correctly placed and tested
- recursive gate rejection covers forbidden claim flags
- docs describe current state rather than stale release-candidate state
- POD gate passed for all ten examples

Claude did not authorize release, measured promotion, broad/whole-app speedup,
public true-zero-copy wording, CuPy performance, Tier-3 support, raw callbacks,
C ABI / non-Python host work, or app-specific kernels.

### Seat 3: Internal Third-Seat Reviewer

Reviewer:

- Dirac
- agent id: `019efc3d-ada6-7130-907b-51ef4face6dc`

Verdict:

- `accept_goal4621_complete_not_release`

Summary:

- Catalog/front door separates five measured surfaces from one weighted-sum
  candidate.
- Candidate status remains unpromoted.
- All non-authorization flags remain false.
- Recursive regression gate rejects forbidden claim flags.
- GPU evidence passes ten of ten examples with `release_authorized: False`.
- No release, promotion, true-zero-copy, CuPy, Tier-3, raw callback, C ABI,
  non-Python host, or app-specific-kernel authorization is granted.

## Antigravity Review Debt

Antigravity CLI was attempted but returned exit code `0` with empty stdout.

Debt record:

- `future/v4/reviews/antigravity_v4_goal4621_catalog_hardening_completion_review_blocked_2026-06-24.md`

Raw attempted files:

- `future/v4/reviews/antigravity_v4_goal4621_catalog_hardening_completion_review_2026-06-24.raw.md`
- `future/v4/reviews/antigravity_v4_goal4621_catalog_hardening_completion_review_2026-06-24.stderr.txt`

This Antigravity debt is not counted as a completed external review. It can be
backfilled later through Antigravity GUI or a working CLI path.

## Verification

Local:

```text
py -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_catalog_regression_gate_test tests.v4_fixed_radius_docs_and_example_test tests.v4_point_group_nearest_witness_device_outputs_validation_test
Ran 43 tests ... OK
```

Local dry-run gate:

- `future/v4/evidence/v4_goal4621_catalog_dry_run_hardened_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4621_catalog_dry_run_hardened_include_candidates_2026-06-24.md`
- status: `passed`
- examples: `10`

POD:

- GPU: NVIDIA RTX A5000
- driver: `570.195.03`

POD tests:

```text
python3 -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_catalog_regression_gate_test
Ran 34 tests ... OK
```

POD GPU catalog gate:

- `future/v4/evidence/v4_goal4621_catalog_gpu_hardened_include_candidates_32768_2026-06-24.json`
- `future/v4/evidence/v4_goal4621_catalog_gpu_hardened_include_candidates_32768_2026-06-24.md`
- status: `passed`
- mode: `gpu`
- examples: `10`
- release authorized: `false`

## Goal-Level Decision Audit

1. Am I being foolish by marking `goal4621` complete?
   No. This is a narrow catalog/front-door hardening completion with local,
   POD, Claude, and third-seat evidence.
2. What would make this decision foolish?
   Treating catalog hardening as V4 release, measured promotion, or public
   true-zero-copy authorization.
3. Is there another path that avoids being stuck on one thought?
   Yes. Keep the completion narrow and proceed to `goal4622`, which is only a
   Tier-3 protocol, not callback support.
4. Can I start a different path that actually solves the problem?
   Yes. The next useful path is `goal4622`: define the constrained callback
   spike protocol so complex user callback expectations are bounded before any
   implementation is attempted.

## Non-Authorization

This consensus does not authorize:

- V4 release
- V4 release-candidate status
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- public true-zero-copy wording
- OptiX 9.1 claims
- CuPy performance claims
- Tier-3 callback support
- raw OptiX callback support
- C ABI / embedding / non-Python-host work
- app-specific native kernels

## Next Goal

Proceed to `goal4622`:

- Tier-3 callback spike protocol
- falsifiable constraints for scalar per-hit reduce callbacks
- explicit rejection of action-shaped callbacks
- no Tier-3 support claim

