# Goal2398 RT-DBSCAN Clean Pod Evidence After Union Repair

Date: 2026-05-19

Status: clean RTX A5000 pod evidence for Goal2397 repair

## Environment

Artifacts:

```text
docs/reports/goal2398_rt_dbscan_clean_pod_evidence/
```

The pod runner was executed from a clean checkout of:

```text
7b9cd29afd02c9790b8982b9d99423b34661d278
```

Hardware and runtime recorded by `environment.txt`:

```text
Python 3.12.3
NVIDIA RTX A5000, driver 570.211.01
CuPy 14.0.1
```

The pod command supplied by the user was for `root@69.30.85.177 -p 22055`; this
run used the project working key `id_ed25519_rtdl_codex_current_pod`.

## Results

| Dataset | Points | Mode | Seconds | Candidate edges | Correctness check | Boundary |
| --- | ---: | --- | ---: | ---: | --- | --- |
| `tiny` | 9 | CPU reference | 0.000111 | 12 | self-reference pass | CPU smoke |
| `tiny` | 9 | RTDL CPU rows | 0.000147 | 33 rows | matches CPU reference | generic row smoke |
| `clustered3d` | 4096 | host-bucket CuPy continuation | 1.983031 | 1,055,360 | same signature as device grid | old host-index debt |
| `clustered3d` | 4096 | repaired CuPy device grid | 0.500779 | 1,055,360 | same signature as host bucket | CUDA-core partner baseline |
| `road3d` | 4096 | host-bucket CuPy continuation | 0.949524 | 331,652 | same signature as device grid | old host-index debt |
| `road3d` | 4096 | repaired CuPy device grid | 0.490753 | 331,652 | same signature as host bucket | CUDA-core partner baseline |
| `ngsim_dense` | 4096 | repaired CuPy device grid | 0.545176 | 41,873 | no CPU validation in timed row | CUDA-core partner baseline |
| `clustered3d` | 1024 | OptiX prepared rows | 1.521349 | 131,244 rows | no CPU validation in timed row | RT-core traversal, host row materialization |
| `road3d` | 1024 | OptiX prepared rows | 1.191120 | 42,104 rows | no CPU validation in timed row | RT-core traversal, host row materialization |

Speedups of the repaired device-grid continuation over the old host-bucket
continuation:

```text
clustered3d 4096: 1.983031 / 0.500779 = 3.96x
road3d 4096:     0.949524 / 0.490753 = 1.93x
```

## Interpretation

Goal2397 solved the immediate pathological component-continuation problem. The
generic CuPy device-grid radius-graph component primitive now finishes the
4096-point clustered row that previously timed out on the pod.

The repaired primitive is still a CUDA-core partner baseline. It is not an
RT-core speedup claim; in other words: not an RT-core speedup claim.

The OptiX prepared-row artifacts prove that the generic RT-core traversal path
builds and runs on the RTX A5000 pod. They also show the remaining RT-DBSCAN gap:
the current OptiX path materializes neighbor rows on the host before component
continuation. The paper-style next step is still a generic bridge from OptiX
fixed-radius device output to device-resident grouped/component continuation.
Short name: OptiX fixed-radius device output to device-resident grouped/component continuation.

## Verdict

Goal2398 is `accept-with-boundary`.

- Accept: the repair is reproducible from a clean pushed commit, the pod runner
  completes, and the repaired CuPy device-grid primitive gives a fairer and much
  faster CUDA-core continuation baseline.
- Boundary: no RT-DBSCAN paper reproduction, paper-speedup claim, broad RT-core
  speedup claim, or v2.x release claim is authorized by this evidence alone.
