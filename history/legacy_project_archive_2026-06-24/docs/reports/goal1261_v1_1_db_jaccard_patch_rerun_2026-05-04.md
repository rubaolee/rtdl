# Goal1261 v1.1 DB/Jaccard Patch Rerun

Date: 2026-05-04

Valid: `True`
Public wording authorized: `False`
Release gate authorized: `False`

This report records a targeted pod rerun after two v1.1 fixes:

1. Raise the native Embree/OptiX DB candidate ceiling from `250000` to
   `1000000`, matching the existing DB row ceiling.
2. Change polygon-set Jaccard summary chunk policy from `512-4096` to
   `1024-4096`, and change the default chunk size to `1024`.

Vulkan, HIPRT, and Apple RT were not changed.

## Patch Scope

Code paths changed:

- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal877_polygon_overlap_optix_phase_profiler.py`
- `scripts/goal1257_v1_1_embree_optix_pod_executor.sh`
- `tests/goal877_polygon_overlap_optix_phase_profiler_test.py`

Follow-up packet cleanup also moved active future Jaccard pod commands from
chunk `512` to chunk `1024` so old packet generators do not recreate the
Goal1260 failure. Historical reports remain unchanged.

## Pod Rerun

Artifacts:

- directory: `docs/reports/goal1261_patch_rerun_2026-05-04/`
- source base: Goal1257 staged source on RTX A5000 pod
- GPU: NVIDIA RTX A5000
- driver: `580.126.09`
- CUDA: `13.0`
- Python: `3.12.3`

Commands rerun:

```text
python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario all --copies 100000 --iterations 5 --output-mode compact_summary --strict
python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario all --copies 100000 --iterations 5 --output-mode compact_summary --strict
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary
```

## Results

| Row | Status Before | Status After | Evidence |
| --- | --- | --- | --- |
| `database_analytics` Embree 100k | failed, `250000` candidate ceiling | pass | `db_embree_100000.json` |
| `database_analytics` OptiX 100k | failed, `250000` candidate ceiling | pass | `db_optix_100000.json` |
| `polygon_set_jaccard` OptiX 8192 | failed parity at chunk `512` | pass parity at default chunk `1024` | `polygon_jaccard_optix_8192.json` |

## Timing

Ratios below are `OptiX / Embree`; values below `1.0` mean OptiX is faster.

| DB 100k phase | Embree sec | OptiX sec | Ratio |
| --- | ---: | ---: | ---: |
| one-shot total | `10.916075` | `10.223091` | `0.937` |
| prepared-session prepare total | `8.829994` | `7.193207` | `0.815` |
| warm query median | `0.912539` | `1.263886` | `1.385` |

Jaccard 8192 default chunk after patch:

| Field | Value |
| --- | ---: |
| chunk copies | `1024` |
| chunk count | `8` |
| parity vs CPU | `true` |
| OptiX candidate discovery sec | `1.711265` |
| native exact continuation sec | `2.138473` |

## Interpretation

The DB 100k blocker is removed as a correctness/execution blocker for Embree
and OptiX. It is not a strong app-level speedup result: OptiX is modestly faster
for one-shot total and prepare, but slower for warm-query median. This supports
continued v1.1/v1.5 work on reducing host-side and prepared-session overhead.

The Jaccard 8192 parity blocker is removed for chunk `1024`. Chunk `512` is now
diagnostic-only because Goal1260 live evidence showed it can miss candidates on
the RTX A5000 path. This narrows the reviewed safe chunk policy instead of
overclaiming the old range.

## Remaining Boundaries

- No public RTX speedup wording is authorized by this report.
- DB evidence is compact-summary only, not SQL/DBMS behavior or broad database
  acceleration.
- Jaccard evidence is native-assisted candidate discovery plus native exact
  continuation, not a monolithic GPU Jaccard kernel or whole-app speedup.
- Candidate count diagnostics can still differ from analytic candidate counts
  while parity passes; correctness is judged by summary parity under the current
  profiler contract.

## Next Work

1. Rerun the full Goal1257 matrix with the patched executor if pod time remains.
2. Generate a new intake replacing Goal1260's stale failed rows with patched
   evidence.
3. Send the updated v1.1 performance interpretation to external AI review before
   any public wording or release-gate decision.
