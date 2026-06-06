# Goal3663 RayJoin PIP Batch Executor Cross-Slice Confirmation

Date: 2026-06-06

Status: internal v2.9 performance confirmation; not release or public speedup
authorization.

## Purpose

Goal3660 showed that the reusable generic prepared point/closed-shape batch
count executor gives strong PIP repeated-request throughput on the public
`br_county_start256_count512` slice. Goal3663 checks whether the same contract
survives a larger public-CDB slice rather than only the original 512-row case.

This remains a batched repeated-request throughput contract: not one-shot latency, not full RayJoin paper reproduction, and not public RTDL-beats-RayJoin wording.

## Evidence

Artifacts:

- 512 slice: `docs/reports/goal3660_rayjoin_pip_batch_executor_throughput_a5000/summary.json`
- 4096 slice: `docs/reports/goal3663_rayjoin_pip_batch_executor_cross_slice_a5000/summary_4096.json`

Pod:

- NVIDIA RTX A5000, driver `580.126.09`
- 512 evidence commit: `def665eb`
- 4096 evidence commit: `af35407e`
- Both runs: `source_dirty: []`
- Batch protocol: `--rtdl-pip-batch-request-count 100`,
  `--rtdl-pip-batch-stream-count auto`, `--rtdl-pip-device-predicate-eps 1e-9`

## Results

| Slice | Exact count | RayJoin query ms | RTDL ms/request | RTDL total ms | RayJoin wall ms | RTDL/RayJoin query ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `br_county_start256_count512` | 1417 | 0.192133 | 0.034225 | 1027.254 | 6721.356 | 0.178x |
| `br_county_start0_count4096` | 11331 | 0.460747 | 0.051139 | 1535.243 | 15914.937 | 0.111x |

## Interpretation

The larger 4096-slice result confirms that Goal3660 was not a one-slice
accident. The reusable generic batch executor continues to win the measured
batched-throughput contract:

- The exact PIP positive count matches the validated prepared-count oracle.
- RTDL stays below RayJoin reported query timing on a per-request throughput
  basis.
- RTDL total measured time stays far below RayJoin process wall time for the
  repeated-query protocol.

The result also sharpens the boundary:

- one-shot/sequential PIP remains the honest Goal3658 lane;
- batched repeated-request PIP is the Goal3660/3663 lane;
- full RayJoin paper reproduction remains unauthorized;
- second-GPU confirmation remains future work.

## v2.9 Reading

For the v2.9 internal status table, RayJoin PIP should no longer be described
as a CuPy-owned route. The current reading is:

- RTDL/OptiX beats the prior project-owned CuPy dense baseline on the bounded
  one-shot/sequential scalar-count row;
- RTDL/OptiX strongly wins batched repeated-request throughput on both 512 and
  4096 public-CDB slices;
- RTDL still does not claim one-shot RTDL-beats-RayJoin or whole-app RayJoin
  reproduction.

## Boundary

Goal3663 does not authorize:

- public v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app RayJoin speedup wording;
- RayJoin paper reproduction wording;
- RTDL-beats-RayJoin one-shot wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

## Validation

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3663_rayjoin_pip_batch_executor_cross_slice_test
```

Pod:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk -j2
```
