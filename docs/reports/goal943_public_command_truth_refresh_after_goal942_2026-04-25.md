# Goal943 Public Command Truth Refresh After Goal942

Date: 2026-04-25

## Scope

Goal943 refreshes the public command truth audit after Goal942 expanded the public RTX claim-review command surface.

## Finding

The first audit run found three documented commands that were not mechanically covered by the public command audit:

- `examples/rtdl_road_hazard_screening.py --backend optix --output-mode summary --optix-mode native --require-rt-core`
- `scripts/goal933_prepared_segment_polygon_optix_profiler.py --backend optix --scenario segment_polygon_hitcount_prepared`
- `scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py --backend optix --scenario segment_polygon_anyhit_rows_prepared_bounded`

Those commands are valid documented RTX-gated command shapes, but `scripts/goal515_public_command_truth_audit.py` did not yet list them in the Goal821 require-RT-core coverage map.

## Fix

Updated `scripts/goal515_public_command_truth_audit.py` so the expanded Goal942 RTX claim-review commands are mechanically covered under a separate `goal942_claim_review_command_*` coverage bucket:

- DB compact summary
- Road hazard prepared native summary
- Segment/polygon prepared hit-count profiler
- Segment/polygon prepared bounded pair-row profiler
- Hausdorff threshold decision
- ANN candidate coverage decision
- Barnes-Hut node coverage decision

## Regenerated Artifacts

- `docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

## Verification

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

- `valid: true`
- public docs scanned: `14`
- runnable public commands found: `280`
- uncovered commands: `0`
- Goal942 exact claim-review command coverage: `8`

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal515_public_command_truth_audit_test -v
```

Result: 1 test OK.

## Boundary

This goal verifies documentation command coverage only. It does not run RTX benchmarks and does not authorize public speedup claims.
