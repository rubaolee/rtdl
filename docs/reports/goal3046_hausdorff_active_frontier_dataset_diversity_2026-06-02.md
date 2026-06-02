# Goal3046 Hausdorff Active-Frontier Dataset-Diversity Harness

Date: 2026-06-02

Status: harness landed; A4000 dataset-diversity run passed.

## Purpose

Goal3045 confirmed that the active-frontier Hausdorff path remains faster than
the CuPy grouped-grid reference across repeated same-process trials for the
original dense demo generator. Goal3046 adds a dataset-diversity harness so the
next pod run can test whether that result survives more than one point-set
shape.

The harness is:

- `scripts/goal3046_hausdorff_active_frontier_dataset_diversity.py`

It compares the same two methods as Goal3045:

- `cupy_grouped_grid_rawkernel`
- `rtdl_rt_grouped_active_frontier_nearest_witness`

Each case uses warmup, alternating measurement order, median/IQR summaries, and
per-trial exact-distance validation.

## Dataset Shapes

The first A4000 run is expected to use:

- `demo_offset`: the original dense synthetic generator.
- `clustered_shift`: four shifted Gaussian-like clusters.
- `ring_vs_spiral`: structured curved point sets with anisotropic offset.
- `adversarial_tail_outlier`: a mostly overlapping cloud with a late outlier,
  used to ensure a seed sample that may miss the witness cannot break exactness.

## Boundary

This is internal v2.6 engineering evidence. It does not authorize release,
public speedup wording, broad RT-core speedup wording, whole-app speedup
wording, or true-zero-copy wording.

## A4000 Run

Pod:

- SSH target: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000
- Source commit: `2c7d50bac57e9f370fc09ab0fd6f06567afd412c`

Command shape:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/.venvs/rtdl_goal3042/bin/python \
  scripts/goal3046_hausdorff_active_frontier_dataset_diversity.py \
  --sizes 32768 65536 131072 \
  --trials 5 \
  --warmup 1 \
  --seed-sample-count 1024 \
  --target-points-per-group 512
```

All 60 measured trials matched the exact CuPy grouped-grid distance.

| Dataset | Points | CuPy median sec | Active-frontier median sec | Active speedup vs CuPy |
| --- | ---: | ---: | ---: | ---: |
| `adversarial_tail_outlier` | 32768 | 0.088057114 | 0.039574610 | 2.225x |
| `adversarial_tail_outlier` | 65536 | 0.348891625 | 0.079116690 | 4.410x |
| `adversarial_tail_outlier` | 131072 | 1.274103531 | 0.175881173 | 7.244x |
| `clustered_shift` | 32768 | 0.087490768 | 0.039654803 | 2.206x |
| `clustered_shift` | 65536 | 0.351187654 | 0.078376334 | 4.481x |
| `clustered_shift` | 131072 | 1.291312220 | 0.168302495 | 7.673x |
| `demo_offset` | 32768 | 0.080004114 | 0.039142341 | 2.044x |
| `demo_offset` | 65536 | 0.301974065 | 0.079382825 | 3.804x |
| `demo_offset` | 131072 | 1.101113547 | 0.171910775 | 6.405x |
| `ring_vs_spiral` | 32768 | 0.083853793 | 0.038874922 | 2.157x |
| `ring_vs_spiral` | 65536 | 0.330445877 | 0.078749182 | 4.196x |
| `ring_vs_spiral` | 131072 | 1.207955672 | 0.169599177 | 7.122x |

Summary:

- Minimum median speedup vs CuPy: 2.044x.
- Median of median speedups vs CuPy: 4.303x.
- Maximum median speedup vs CuPy: 7.673x.

Artifact:

- `docs/reports/goal3046_hausdorff_active_frontier_dataset_diversity_a4000_2026-06-02.json`

## Interpretation

Goal3046 reduces the main Goal3045 uncertainty: the positive A4000 crossover is
not limited to the original dense demo generator. The active-frontier path kept
exact-distance parity and faster medians for clustered, curved, and adversarial
tail-outlier cases.

The outlier case also exercises the important correctness boundary: even when a
seed sample can miss the eventual witness, active-frontier remains exact because
the seed only provides a lower-bound radius for pruning. A missed witness stays
active and is resolved by the native nearest-witness pass.

This is still not a public claim packet. It is one GPU, synthetic dataset
diversity, one seed/sample configuration, and one CuPy reference method.
Second-GPU evidence and external review are still required before broader
Hausdorff RT-core wording.
