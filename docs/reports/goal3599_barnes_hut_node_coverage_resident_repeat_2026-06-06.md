# Goal3599 - Barnes-Hut Node-Coverage Resident Repeat Evidence

Date: 2026-06-06

Status: v2.9 internal performance evidence; not release or public speedup authorization.

## Purpose

Goal3536 marked the Barnes-Hut node-coverage row as partial because the comparison harness repeated whole subprocesses and accumulated only about `0.31s` of v2.8 hot-query time. Goal3599 verifies the current v2.9 app-level repeat surface for the same Barnes-Hut node-coverage prepared OptiX contract.

This closes the "silent partial row" problem for the current Barnes-Hut node-coverage path. It does not by itself create a clean v2.9-vs-v2.3 ratio because the v2.3 and old v2.8 roots do not expose the same app-level repeat/warmup surface.

## Artifact

- `docs/reports/goal3599_barnes_hut_node_coverage_resident_repeat_a5000/summary.json`

## Pod Configuration

GPU:

- NVIDIA RTX A5000, driver `580.126.09`

Clean checkout:

- `/root/rtdl_goal3595_clean`
- commit `092e25a4610ac7a02dfad026d473eab9a97cc72c`
- recorded `git_status_short`: empty

Command:

```bash
cd /root/rtdl_goal3595_clean
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3595_clean/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/root/rtdl_goal3595_clean/build/librtdl_optix.so
python3 examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode optix_node_coverage_prepared \
  --body-count 8192 \
  --skip-validation \
  --require-rt-core \
  --repeat 1300 \
  --warmup 20 \
  --json-out /tmp/goal3599_bh_current_1300.json
```

## Result

| Field | Value |
| --- | ---: |
| Body count | 8192 |
| Backend | OptiX |
| RT-core accelerated | true |
| Oracle decision matches | true |
| Oracle identity matches | true |
| Covered body count | 8192 |
| Repeat | 1300 |
| Warmup | 20 |
| Median hot query sec | 0.008080567 |
| Total measured hot query sec | 11.637928869 |
| Scene prepare sec | 0.740880874 |

The run satisfies the v2.9 10-second evidence rule for the current Barnes-Hut node-coverage prepared OptiX contract.

## Comparison To Goal3536

Goal3536 measured the old row through subprocess repeats:

- v2.3 median primary metric: `0.011718154s`;
- v2.8 median primary metric: `0.025249238s`;
- v2.8/v2.3 diagnostic ratio: `0.464x`;
- v2.8 accumulated hot-query time: about `0.309s`;
- both old lanes were marked target-incomplete.

Goal3599 changes the measurement quality for current main:

- current median hot query sec: `0.008080567s`;
- current accumulated hot-query time: `11.637928869s`;
- current path matches the CPU oracle decision and identity;
- current path uses a clean checkout and records an empty git status.

This is a substantial measurement repair and a current-path improvement over the old v2.8 subprocess-repeated median. Because v2.3 does not expose the same resident repeat API, this report does not publish a same-runner v2.9-vs-v2.3 speedup ratio.

## Boundary

Goal3599 does not authorize:

- public v2.9 release wording;
- public speedup wording;
- whole-app Barnes-Hut speedup wording;
- RT-BarnesHut paper reproduction wording;
- broad RT-core speedup wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

The only accepted conclusion is: current v2.9 main has valid app-level resident-repeat evidence for the Barnes-Hut prepared OptiX node-coverage contract, and the old Goal3536 Barnes-Hut row should no longer be treated as silently partial for current-main diagnosis.
