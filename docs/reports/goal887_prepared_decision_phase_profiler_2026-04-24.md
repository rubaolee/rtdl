# Goal887 Prepared Decision Phase Profiler

Date: 2026-04-24

## Result

Goal887 adds a shared cloud-ready phase profiler for the four prepared
fixed-radius decision sub-paths added in Goals879-882:

- `hausdorff_threshold`
- `ann_candidate_coverage`
- `facility_service_coverage`
- `barnes_hut_node_coverage`

The profiler is:

```bash
scripts/goal887_prepared_decision_phase_profiler.py
```

It supports local `dry-run` mode and cloud `optix` mode. The RTX manifest now
uses this profiler for Hausdorff, ANN, facility, and Barnes-Hut deferred
entries instead of raw app CLI commands.

## Phase Contract

The profiler emits schema:

```text
goal887_prepared_decision_phase_contract_v1
```

Required phases:

- `input_build_sec`
- `point_pack_sec`
- `optix_prepare_sec`
- `optix_query_sec`
- `python_postprocess_sec`
- `validation_sec`
- `optix_close_sec`

Each result includes `cloud_claim_contract`, `required_phase_groups`, a
scenario-specific claim scope, and explicit non-claims.

## Claim Boundary

This does not promote the four apps to public RTX speedup claims. It only makes
their prepared decision sub-paths cloud-measurable with phase separation.

Boundaries:

- Hausdorff: threshold decision only, not exact Hausdorff distance.
- ANN: candidate coverage only, not ANN ranking or index performance.
- Facility: service coverage only, not ranked nearest-depot assignment.
- Barnes-Hut: node coverage only, not opening-rule or force-vector reduction.

## Manifest Update

The deferred RTX manifest entries now invoke:

```bash
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ...
```

with `--mode optix`, `--iterations 10`, `--skip-validation`, and per-scenario
output JSON paths under `docs/reports/`.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal887_prepared_decision_phase_profiler_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `17 tests OK`.

Manifest refresh:

```bash
PYTHONPATH=src:. python3 scripts/goal759_rtx_cloud_benchmark_manifest.py \
  --output-json docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json
```

Pre-cloud gate:

```bash
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal887_pre_cloud_readiness_after_profiler_manifest_2026-04-24.json
```

Result: `valid: true`.

