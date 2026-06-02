# Goal3045 Hausdorff Active-Frontier Multitrial Harness

Date: 2026-06-02

Status: harness landed; A4000 multitrial run passed.

## Purpose

Goal3042 produced a strong single-run A4000 result for the active-frontier
Hausdorff path, but the Goal3043 Claude review correctly noted that a public
performance claim needs repeated timing with warmup, medians, and dispersion.

Goal3045 adds `scripts/goal3045_hausdorff_active_frontier_multitrial.py` to run
the current CuPy grouped-grid reference and the RTDL/OptiX active-frontier path
inside one Python process with:

- explicit warmup iterations,
- alternating measurement order,
- per-trial exact-distance validation,
- median, quartile, and IQR summaries,
- closed claim-boundary flags.

## Boundary

This harness is for internal v2.6 evidence. It does not authorize release,
public speedup wording, broad RT-core speedup wording, whole-app speedup
wording, or true-zero-copy wording.

## A4000 Run

Pod:

- SSH target: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000
- Source commit: `afb6240e2f9cadfce8f95b9978fc203c46dfb2d5`

Command shape:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/.venvs/rtdl_goal3042/bin/python \
  scripts/goal3045_hausdorff_active_frontier_multitrial.py \
  --sizes 16384 65536 131072 \
  --trials 10 \
  --warmup 2 \
  --seed-sample-count 1024 \
  --target-points-per-group 512
```

All trials matched the exact CuPy grouped-grid distance.

| Points | CuPy median sec | Active-frontier median sec | Active speedup vs CuPy | CuPy IQR sec | Active IQR sec |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16384 | 0.027996940 | 0.020015929 | 1.399x | 0.003779652 | 0.000837396 |
| 65536 | 0.301261282 | 0.079905885 | 3.770x | 0.000021615 | 0.002523025 |
| 131072 | 1.109387681 | 0.168451022 | 6.586x | 0.009965148 | 0.006480030 |

Artifact:

- `docs/reports/goal3045_hausdorff_active_frontier_multitrial_a4000_2026-06-02.json`

## Interpretation

Goal3045 confirms that the Goal3042 single-run crossover is not just a cold-run
artifact for the tested A4000 setup. After two warmup passes and ten alternating
same-process trials, active-frontier remains faster than CuPy at 16384 points
and scales to a 6.586x median speedup at 131072 points.

The evidence is still bounded. It covers one GPU, one synthetic dense generator,
one seed/sample configuration, and one grouped-grid CuPy baseline. Public
Hausdorff RT-core performance wording still needs external review plus dataset
diversity and second-GPU confirmation.
