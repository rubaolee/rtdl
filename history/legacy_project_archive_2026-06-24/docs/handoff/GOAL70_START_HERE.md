# Goal 70 Start Here

Date: 2026-04-04

## Goal

Goal 70 is the next performance goal after Goal 69.

Objective:
- make the OptiX positive-hit `pip` path beat PostGIS on at least one accepted
  measured package while preserving exact parity

Priority:
1. OptiX
2. Embree later
3. Vulkan later
4. native C oracle remains correctness-only

## Required Reading

Read these first:

1. `docs/reports/goal69_pip_performance_repair_2026-04-04.md`
2. `docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.json`
3. `docs/reports/goal69_final_measured_artifact_note_2026-04-04.md`
4. `docs/reports/postgis_performance_investigation_2026-04-04.md`
5. `docs/reports/postgis_performance_investigation_review_2026-04-04.md`

## Current Measured Baseline

Accepted Goal 69 positive-hit `pip` timings:

### County/Zipcode

- PostGIS: `3.238477414 s`
- Embree: `12.668624839 s`
- OptiX: `15.652318004 s`
- parity:
  - Embree vs PostGIS: `true`
  - OptiX vs PostGIS: `true`

### BlockGroup/WaterBodies

- PostGIS: `0.007254268 s`
- Embree: `0.070980010 s`
- OptiX: `0.069386854 s`
- parity:
  - Embree vs PostGIS: `true`
  - OptiX vs PostGIS: `true`

## Engineering Thesis

The next step is not to change semantics again.

The next step is to profile and reduce OptiX overhead within the already
accepted positive-hit `pip` contract:

- device launch/setup overhead
- candidate bookkeeping overhead
- hit-bitset write cost
- host compaction/materialization cost
- unnecessary marshaling or copies

## Required Boundaries

Do not do these:

- do not weaken parity
- do not change the accepted `full_matrix` default semantics
- do not publish unfinished performance claims
- do not broaden the goal into Embree/Vulkan optimization yet

## First Actions

1. inspect:
   - `src/native/rtdl_optix.cpp`
   - `src/rtdsl/optix_runtime.py`
   - `scripts/goal69_pip_positive_hit_performance.py`
2. profile the current OptiX positive-hit path on Linux
3. identify the dominant cost on:
   - `county_zipcode`
   - `blockgroup_waterbodies`
4. make one focused OptiX optimization pass
5. rerun Goal 69 harness on Linux
6. document:
   - proposal
   - result
   - review
   - rebuttal if needed

## Suggested Command Sequence

```bash
cd /home/lestat/work/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_py_test tests.goal69_pip_positive_hit_performance_test
```

Then inspect and rerun:

```bash
cd /home/lestat/work/rtdl_python_only
PYTHONPATH=src:. RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc \
python3 scripts/goal69_pip_positive_hit_performance.py \
  --county-dir build/datasets/uscounty_top4/uscounty_feature_layer \
  --zipcode-dir build/datasets/uszcta_top4/uszcta_feature_layer \
  --blockgroup-dir build/datasets/tl_2024_23031_bg/feature_layer \
  --waterbodies-dir build/datasets/tl_2024_23031_areawater/feature_layer \
  --output-dir build/goal70_optix_perf \
  --host-label lestat-lx1 \
  --backends optix \
  --cases county_zipcode,blockgroup_waterbodies
```

## Deliverables

Before handing back, produce:

1. a measured summary artifact
2. a short report with exact timings and parity
3. no publish yet unless 2-AI consensus is completed
