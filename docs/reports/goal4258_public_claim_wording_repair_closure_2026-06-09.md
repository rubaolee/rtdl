# Goal4258 Public Claim Wording Repair Closure

Date: 2026-06-09
Status: repaired wording ready for focused re-review

## Purpose

Goal4258 records the closure of the three required wording fixes from the
Goal4255 Claude review of Goal4254. The repaired wording is intended for review
before any formal v2.10 release packet uses it.

## Fixes Applied

| Review Item | Required Fix | Applied Change |
| --- | --- | --- |
| R1 | Replace unanchored `strong OptiX benefits`. | Goal4254 now says `measured OptiX speedups over same-contract CPU or partner baselines`. |
| R2 | Avoid making partner usage sound benchmark-only. | Goal4254 now says partners are used `where custom continuation logic is needed`. |
| R3 | Avoid POSIX-only `PYTHONPATH=src:.` in candidate front-page text. | Goal4254 now says `used from the source tree; see the README for platform-specific setup`. |
| Recommended clarity | Soften `scoped by contract and artifact`. | Goal4254 now says `scoped to specific workload contracts and reviewed timing artifacts`. |

## Validation

Local focused validation:

```text
Ran 14 tests in 0.216s

OK
```

Pod focused validation on RTX 4000 Ada at source commit `b24a561d`:

```text
Ran 14 tests in 0.089s

OK
```

The pod validation covered:

- `tests.goal4254_v2_10_public_claim_wording_candidate_test`
- `tests.goal4257_v2_10_release_candidate_packet_draft_test`
- `tests.goal4251_v2_10_internal_release_prep_packet_test`
- `tests.goal4248_current_public_docs_claim_boundary_scan_test`

## Boundary

Goal4258 closes wording repairs only. It does not authorize release, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
RTDL-beats-RayJoin wording, paper-reproduction wording, package-install wording,
true-zero-copy wording, automatic partner/backend selection, AMD/HIPRT
performance wording, or app-specific native-engine logic.
