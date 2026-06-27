# V3.0 Performance Release Gate Plan

Date: 2026-06-20

Status: V3-only execution plan. Focuses only on V3 runtime and performance
surfaces. Excludes external-host, packaging, SDK, generated-binding, and
cross-language integration claims.

## Purpose

The reopened V3 goal is to prove or repair V3 as RTDL's highest-performance
independent-language release line.

This requires a claim-grade V3 performance matrix, not only:

- source-tree doctor success;
- `v3_current` unit/regression success;
- ten-app route-health execution;
- old internal performance reports.

## Runner Classification

| Runner | Classification | Use in V3 performance release |
| --- | --- | --- |
| `scripts/goal2626_benchmark_embree_optix_baseline.py` | Claim-matrix base | Primary current V3 OptiX-vs-Embree standard matrix for promoted benchmark apps. |
| `scripts/goal2636_strengthen_benchmark_rows.py` | Claim-matrix supplement | Strengthened/stress ladders for historically weak rows: Hausdorff, Spatial RayJoin, RTNN, Barnes-Hut, Triangle. |
| `scripts/rtdl_human_scale_rt_vs_embree_comparison.py` | Claim-grade calibration gate | Human-scale 1-10s hot-query aggregate packet; good public-row candidate but currently inherits v2.14 calibration assumptions and must be checked on current V3. |
| `scripts/goal3828_current_benchmark_scale_profile_runner.py` | Route-health gate | Confirms current ten benchmark routes execute and claim flags remain false; not enough for V3 performance release. |
| `scripts/run_test_matrix.py --group v3_current` | Regression gate | Confirms source-tree V3 current test surface; not a performance matrix. |
| `scripts/rtdl_source_tree_doctor.py --json` | Environment/front-door gate | Confirms dependencies/docs/front-door health; not a performance matrix. |

## Minimum V3 Performance Gate

A V3 performance release candidate must pass:

1. `scripts/rtdl_source_tree_doctor.py --json`
2. `scripts/run_test_matrix.py --group v3_current`
3. `scripts/goal2626_benchmark_embree_optix_baseline.py --scale standard --build-native`
4. `scripts/goal2636_strengthen_benchmark_rows.py --tier standard --build-native`
5. `scripts/rtdl_human_scale_rt_vs_embree_comparison.py`

The gate is not accepted if the only passing command is the route-health runner.

## Stress Gate

If the minimum gate is clean or nearly clean, run:

```bash
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier stress \
  --artifact-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/goal2636_stress \
  --timeout-sec 3600 \
  --build-native
```

## Route-Health Gate

Run this only as supporting evidence:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python3 scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --materialize-rayjoin-public-cdb \
  --rayjoin-public-cdb-dir /tmp/rtdl_v3_perf_rayjoin_public_cdb \
  --output-json docs/reports/v3_0_performance_release_candidate_2026-06-20/current_scale_profile.json \
  --output-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/current_scale_outputs \
  --timeout-scale 2.5 \
  --heartbeat-sec 60 \
  --stdout-tail 12000 \
  --stderr-tail 8000
```

This gate remains route-health only because it explicitly sets public speedup
claim flags to false.

## Acceptance Rules

Each promoted app row must become one of:

| Status | Meaning |
| --- | --- |
| `release_ready` | Same-contract, current-code, pod-run, correctness-validated, phase-split, repeated, artifact-backed. |
| `needs_repair` | Runner or implementation must be fixed before V3 performance release. |
| `internal_only` | Useful evidence but not public release wording. |
| `demote` | Not part of the V3 performance release matrix. |

The final V3 performance release cannot rely on wording to cover a failed row.

## Initial Risk Rows

| App | Risk |
| --- | --- |
| Barnes-Hut | Current route closure is mixed-explicit; RT-native hierarchical traversal remains future optional research. Needs current same-contract node-coverage proof and clear boundary. |
| Triangle Counting | Prior graph/capture wording was fail-closed; current proof must be non-graph/same-contract and not paper-scale overclaim. |
| RT-DBSCAN | Partner continuation can dominate; must separate RT threshold stage from Numba/CuPy continuation. |
| Spatial RayJoin | PIP, LSI, and overlay-seed must remain separate; no full RayJoin paper reproduction unless exact packet exists. |
| Contact Manifold | Small scale can favor CPU; release row should use scale where broadphase contract is meaningful and validated. |

## Immediate Pod Command Set

Use a fresh artifact directory:

```bash
set -euo pipefail
cd /workspace/rtdl_v0_4_release_prep_review
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so

python3 scripts/rtdl_source_tree_doctor.py --json \
  > docs/reports/v3_0_performance_release_candidate_2026-06-20/source_tree_doctor.json

python3 scripts/run_test_matrix.py --group v3_current \
  > docs/reports/v3_0_performance_release_candidate_2026-06-20/v3_current.stdout.txt \
  2> docs/reports/v3_0_performance_release_candidate_2026-06-20/v3_current.stderr.txt

python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --artifact-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/goal2626_standard \
  --timeout-sec 1800 \
  --build-native

python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier standard \
  --artifact-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/goal2636_standard \
  --timeout-sec 2400 \
  --build-native

python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py \
  --output-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/human_scale
```

## Expected Output

The next report must answer:

1. Does current V3 beat Embree/CPU on the same-contract rows?
2. Does it beat or match V2.14's released performance matrix?
3. Which rows are release-ready, internal-only, or broken?
4. Which code/harness fixes are required before calling V3 the
   highest-performance independent-language release?
