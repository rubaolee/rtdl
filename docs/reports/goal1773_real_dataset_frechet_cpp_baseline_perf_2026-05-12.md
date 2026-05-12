# Goal1773 Real Dataset Continuous Frechet C++ Baseline Perf

Date: 2026-05-12
Status: diagnostic benchmark
Verdict: needs-more-work

## Purpose

This report follows up the Goal1771 continuous Frechet Python+RTDL learner app
with a more serious baseline. Pure Python all-cells timing is not an acceptable
performance baseline once the RT path is known to beat it on synthetic cases.

This benchmark therefore compares:

- a compiled C++ `-O3` all-cells continuous Frechet distance-search baseline,
- the current Python+RTDL OptiX broadphase learner path with
  `--require-rt-core` semantics and no pure-Python oracle timing inside the
  timed loop.

## Public Dataset Search

Candidate datasets found:

- Microsoft GeoLife GPS Trajectories 1.3: official Microsoft Download Center,
  17,621 trajectories, about 1.2 million km and 48,000+ hours, 298.7 MB.
- T-Drive taxi trajectories: Beijing taxi trajectories, Kaggle mirror reports
  10,357 taxis and about 15 million points.
- OpenTrace/WorldTrace on Hugging Face: very large global GPS trajectory
  dataset, 2.45 million trajectories and 880 million processed points, 35 GB.

GeoLife was chosen first because it is large enough, real, publicly documented,
and small enough to download and parse quickly on the available pod.

Downloaded on pod:

```text
/root/datasets/geolife/geolife_trajectories_1_3.zip
size: 299 MB
.plt files observed: 18,670
```

## Pod And Setup

Pod:

```text
GPU: NVIDIA RTX A5000
driver: 570.195.03
CUDA: 12.4
OptiX headers: NVIDIA/optix-dev pinned to v9.0.0
RTDL OptiX library: /root/rtdl/build/librtdl_optix.so
```

Dataset pair:

```text
GeoLife user: 000
file A: 20081023025304.plt
file B: 20081026134407.plt
raw points used before downsampling: 908 vs 745
projection: local equirectangular meters from file A start point
distance-search iterations: 8
repeats: 3
```

## Results

| Points per curve | C++ all-cells median wall (s) | RTDL/OptiX broadphase median wall (s) | RT / C++ speed | Candidate cells on last RT search |
| ---: | ---: | ---: | ---: | ---: |
| 128 | 0.007580 | 0.389067 | 0.019x | 14,479 |
| 256 | 0.028080 | 1.552472 | 0.018x | 58,680 |
| 512 | 0.109129 | 7.185207 | 0.015x | 258,566 |

For this real GeoLife pair, the current learner path is not competitive with a
compiled C++ all-cells baseline.

## Interpretation

The result is negative but useful:

- The current RTDL role is only a segment/expanded-shape broadphase.
- On this GeoLife pair, the broadphase prunes very little: at 512 points per
  curve, the last RT search still carries 258,566 candidate cells out of about
  261k possible segment-pair cells.
- The remaining Frechet free-space dynamic program is Python-owned, so even
  modest pruning is not enough to beat a compiled C++ all-cells implementation.
- The 512-point RT path also produced a different distance estimate than the
  C++ all-cells baseline in this diagnostic harness, so this path needs a
  stronger correctness audit before any real-dataset performance claim.

## Verdict

Do not claim real-dataset continuous Frechet acceleration from the current
v1.8 learner app.

The v1.8 learner result remains valuable as a programming-language example:
users can write a new Python+RTDL application and route a generic RT-shaped
broadphase through OptiX RT cores. But real performance against a high-quality
CPU baseline requires more work, most likely one of:

- native C++ continuation for the Frechet free-space decision over candidate
  cells,
- a more selective and proven-conservative free-space-cell filter,
- a prepared/batched OptiX path that amortizes launches across many trajectory
  pairs,
- a separate C++/CUDA baseline harness for broader real-dataset evaluation.

## External AI Task Message

The short task message for independent Claude/Gemini learner versions was saved
locally at:

```text
scratch/goal1773_external_ai_task.txt
```

Message:

```text
Claude/Gemini task: independently write a v1.8 Python+RTDL learner version of continuous Frechet distance over real GPS polylines, keeping RTDL as a generic segment/shape or ray-shaped broadphase only, preserving Python-owned Frechet free-space semantics, and explicitly compare against a compiled/non-Python baseline rather than a slow pure-Python timing baseline; document claim boundaries and do not add app-specific native engine symbols.
```
