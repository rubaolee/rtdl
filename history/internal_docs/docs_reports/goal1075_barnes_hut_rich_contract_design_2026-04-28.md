# Goal1075 Barnes-Hut Rich Node-Coverage Contract

Date: 2026-04-28

## Problem

Goal1071 showed that the current Barnes-Hut `node_coverage_prepared` contract is
not useful for RTX timing. It builds only four one-level quadtree nodes, so the
1M-body RTX query median was only 0.004204 s. Scaling body count under that
contract mostly measures Python input construction and point packing, not
meaningful RT traversal.

## Local Change

This goal keeps the historical one-level path compatible, but adds optional
contract controls:

- `examples/rtdl_barnes_hut_force_app.py`
  - Adds `build_fixed_depth_quadtree_cells(...)`.
  - Extends `node_coverage_oracle(...)` with a configurable `threshold`.
- `scripts/goal887_prepared_decision_phase_profiler.py`
  - Adds `--barnes-tree-depth`.
  - Adds `--hit-threshold`.
  - Records both values in the output artifact.
  - Uses the old one-level tree only when `--barnes-tree-depth 1` and
    `--hit-threshold 1`, preserving prior behavior.

## Dry-Run Evidence

Ran:

```bash
PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario barnes_hut_node_coverage \
  --mode dry-run \
  --body-count 1024 \
  --iterations 1 \
  --radius 0.1 \
  --barnes-tree-depth 6 \
  --hit-threshold 4 \
  --output-json docs/reports/goal1075_barnes_hut_rich_contract_dry_run_2026-04-28.json
```

Result:

- body count: 1,024
- node count: 4,096
- tree depth: 6
- hit threshold: 4
- min candidate count: 4
- max candidate count: 8
- oracle decision: all bodies covered
- CPU reference time: 0.217553 s

## Next Pod Candidate

The next Barnes-Hut pod candidate should not reuse the four-node contract. A
claim-review candidate should use a richer node set and threshold, for example:

```bash
python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario barnes_hut_node_coverage \
  --mode optix \
  --body-count 1000000 \
  --iterations 5 \
  --radius 0.1 \
  --barnes-tree-depth 8 \
  --hit-threshold 4 \
  --skip-validation \
  --output-json docs/reports/goal1075_barnes_hut_rich_contract_rtx_timing.json
```

Before public wording can change, this needs a separate smaller validation row
without `--skip-validation`, cloud evidence, artifact intake, and 2+ AI review.

## Boundary

This goal is local contract preparation only. It does not run cloud, authorize
release, change public wording, or authorize public RTX speedup claims.
