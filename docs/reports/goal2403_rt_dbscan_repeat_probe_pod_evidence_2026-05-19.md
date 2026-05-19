# Goal2403 RT-DBSCAN Repeat Probe Pod Evidence

Date: 2026-05-19

Status: clean RTX A5000 repeat-probe evidence for the Goal2400/2401
OptiX-summary-to-CuPy-component bridge

## Environment

Artifacts:

```text
docs/reports/goal2403_rt_dbscan_repeat_probe_pod/
```

The repeat probe was executed from a clean checkout of:

```text
86856bb37f0f2a8d2f03b3677435b3988f646599
```

Hardware and runtime recorded by `environment.txt`:

```text
Python 3.12.3
NVIDIA RTX A5000, driver 570.211.01
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2392_pod/build/librtdl_optix.so
```

## Results

The probe runs the same 4096-point workload four times in one Python process.
This separates cold setup behavior from warm steady-state behavior.

### Clustered3d

| Repeat | Pure CuPy device-grid seconds | OptiX summaries + CuPy continuation seconds | OptiX summary seconds | CuPy continuation seconds |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.611150 | 0.880737 | 0.862292 | 0.008425 |
| 2 | 0.019493 | 0.049820 | 0.031403 | 0.008290 |
| 3 | 0.019171 | 0.072401 | 0.052058 | 0.008952 |
| 4 | 0.019315 | 0.059749 | 0.040627 | 0.008705 |

### Road3d

| Repeat | Pure CuPy device-grid seconds | OptiX summaries + CuPy continuation seconds | OptiX summary seconds | CuPy continuation seconds |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.488987 | 0.866927 | 0.853830 | 0.003342 |
| 2 | 0.011193 | 0.031441 | 0.019537 | 0.002973 |
| 3 | 0.013758 | 0.048658 | 0.036496 | 0.003204 |
| 4 | 0.014322 | 0.031562 | 0.019699 | 0.002939 |

Both JSON artifacts report `signatures_match=true`. The OptiX bridge rows also
report `rt_core_accelerated=true` and `materializes_neighbor_rows=false`.

## Interpretation

Goal2403 gives the useful missing timing view from Goal2401:

- The first call is dominated by cold setup, including CUDA/CuPy context work
  and OptiX/prepared-path setup.
- Repeats 2-4 show the bridge much closer to the pure CuPy device-grid path.
- The pure CuPy device-grid path remains faster on these two synthetic 4096
  point rows.
- The OptiX bridge still proves an important composition shape: generic RT-core
  fixed-radius summaries can feed a generic partner component continuation
  without O(edges) neighbor-row materialization.

The remaining performance gap is now precise. The bridge needs cheaper repeated
OptiX summary execution or a stronger device-resident output handoff. This is a
generic runtime problem, not a reason to add DBSCAN-specific native ABI.

## Claim Boundary

Goal2403 is `accept-with-boundary`.

- Accept: the repeat probe confirms correctness signatures and shows warm
  steady-state behavior for the generic OptiX-summary-to-CuPy-continuation
  bridge.
- Boundary: this is not paper reproduction, not a paper-speedup claim, and not
  a broad RT-core DBSCAN acceleration claim. The current evidence says the
  bridge is architecturally useful but not yet faster than the optimized pure
  CuPy device-grid continuation on the measured synthetic rows.

Short form: the bridge is not yet faster than the optimized pure CuPy device-grid baseline.
