# Goal1162 Polygon Gate Artifact Replayability

Date: 2026-04-30

## Purpose

Goal1162 improves the polygon pair-overlap and polygon-set Jaccard RTX gate
artifact contract before the next pod batch. The apps already expose the intended
RT structure: OptiX performs LSI/PIP candidate discovery, and native C++
continuation performs exact bounded grid-cell area/Jaccard refinement. The gap
addressed here is replayability of the gate artifact, not a new public speedup
claim.

## Changes

- Updated `scripts/goal877_polygon_overlap_optix_phase_profiler.py` to emit:
  - `schema_version: goal877_polygon_overlap_optix_phase_contract_v2`
  - `source_commit`
- Updated the profiler CLI to create parent output directories before writing
  JSON artifacts.
- Extended `tests/goal877_polygon_overlap_optix_phase_profiler_test.py` to
  enforce the schema/source metadata and directory creation behavior.

## Local Evidence

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal877_polygon_overlap_optix_phase_profiler_test \
  tests.goal1131_polygon_app_phase_contract_test -q
```

Result:

```text
Ran 11 tests in 0.353s
OK
```

Dry-run artifacts:

- `docs/reports/goal1162_polygon_pair_overlap_gate_dry_run_2026-04-30.json`
- `docs/reports/goal1162_polygon_set_jaccard_gate_dry_run_2026-04-30.json`

| Artifact | Status | Schema | Source Commit | Copies | Output | Validation |
|---|---|---|---|---:|---|---|
| pair overlap | pass | v2 | present | 100 | summary | analytic_summary |
| set Jaccard | pass | v2 | present | 100 | summary | analytic_summary |

## Boundary

This goal does not run OptiX locally, does not run cloud, and does not authorize
public RTX speedup wording. It only improves the artifact contract for the next
consolidated RTX pod run.

## Next Step

After external review, keep both polygon commands in the next consolidated pod
batch. Do not start a pod just for this goal.
