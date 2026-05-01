# Goal1161 Hausdorff Non-Analytic Threshold Contract

Date: 2026-04-30

## Purpose

Goal1161 repairs the Hausdorff RTX pre-cloud evidence gap identified by the
earlier scale-contract audit. The previous large Hausdorff candidate used the
authored four-point tiled fixture with an analytic oracle, so increasing
`copies` created many logical points but did not create a meaningful
same-semantics benchmark contract.

This goal adds a deterministic non-analytic Hausdorff threshold-decision
contract. It is intended for local dry-run validation now and a later real RTX
OptiX run in a batched pod session.

## Changes

- Added `scripts/goal1161_hausdorff_nonanalytic_threshold_contract.py`.
- Added `tests/goal1161_hausdorff_nonanalytic_threshold_contract_test.py`.
- Generated local dry-run artifact:
  `docs/reports/goal1161_hausdorff_nonanalytic_threshold_contract_dry_run_2026-04-30.json`.

## Local Evidence

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1161_hausdorff_nonanalytic_threshold_contract_test -q
```

Result:

```text
Ran 3 tests in 0.354s
OK
```

Dry-run command:

```bash
PYTHONPATH=src:. python3 scripts/goal1161_hausdorff_nonanalytic_threshold_contract.py \
  --mode dry-run \
  --point-count 2048 \
  --iterations 1 \
  --output-json docs/reports/goal1161_hausdorff_nonanalytic_threshold_contract_dry_run_2026-04-30.json
```

Dry-run result:

| Field | Value |
|---|---:|
| valid | true |
| point_count_a | 2048 |
| point_count_b | 2048 |
| radius | 0.35 |
| covered_a_to_b | 1861 |
| covered_b_to_a | 1861 |
| within_threshold | false |
| validation_sec | 0.43514154094737023 |

## Boundary

This goal does not run cloud, does not run real OptiX locally, does not
authorize public RTX speedup wording, and does not claim exact Hausdorff
distance. It only makes Hausdorff eligible for a future real RTX batch by
replacing the old analytic tiled benchmark contract with a non-analytic
threshold-decision contract.

## Next Step

Seek external Gemini or Claude review. If accepted, add the Goal1161 OptiX mode
command to the next consolidated RTX pod batch instead of launching a pod just
for Hausdorff.
