# Goal5130 - X-HD Paper Target Matrix

## Verdict

`xhd_paper_target_matrix_ready`

## Purpose

This goal turns the X-HD paper from a broad "full reproduction" wish into a
bounded target matrix. It does not implement another RTDL route and does not
claim any new correctness or performance result.

The output artifact is:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
```

## Source Basis

- Paper: `X-HD: Fast Hausdorff Distance Computation with Ray Tracing`
- DOI: `10.1145/3797905.3800509`
- PDF: `https://rubaolee.github.io/paper_pdfs/2026-xhd.pdf`
- Author repository: `https://github.com/pwrliang/X-HD`
- Pinned author commit from the app manifest:
  `7bf41c8442d059c94f4178355c6d5a10571d9658`

The paper itself lists the source code URL and states the evaluation uses
NVIDIA RTX 3090 for GPU methods, with GPU timing starting after datasets are
loaded onto the GPU and stopping when HD is produced.

## Dataset Targets

The paper target matrix records the dataset families from Table 1:

| Family | Category | Dim | Paper size/statistic | Current target status |
| --- | --- | ---: | --- | --- |
| BraTS | MRI | 3D | 494 images; avg 1.5M non-empty voxels; avg Gini 0.14 | possible Level B only after licensed access; exact blocked |
| USCounty | Geospatial | 2D | 9.4M points; Gini 0.77 | Level B candidate; exact blocked |
| USZipcode | Geospatial | 2D | 43.9M points; Gini 0.61 | Level B candidate; exact blocked |
| Lakes | Geospatial | 2D | 301.7M points; Gini 0.76 | large Level B candidate; not first target |
| Parks | Geospatial | 2D | 403.7M points; Gini 0.76 | large Level B candidate; not first target |
| USWater | Geospatial | 2D | 22.8M points; Gini 0.61 | Level B candidate; exact blocked |
| USCensus | Geospatial | 2D | 52.3M points; Gini 0.65 | Level B candidate; exact blocked |
| All Nodes | Geospatial | 2D | 2.7B points, partially used | not a first target; subset unknown |
| Dragon | Graphics | 3D | 0.4M points; Gini 0.42 | best first Level B candidate |
| AsianDragon | Graphics | 3D | 3.6M points; Gini 0.38 | Level B candidate |
| HappyBuddha | Graphics | 3D | 0.5M points; Gini 0.46 | best first Level B candidate |
| ThaiStatuette | Graphics | 3D | 4.9M points; Gini 0.47 | Level B candidate |

## Figure / Table Targets

The matrix separates paper targets rather than collapsing them into one vague
"full reproduction" label:

| Target | Subject | Required evidence |
| --- | --- | --- |
| Table 1 | dataset sizes and Gini statistics | exact or same-source input provenance, preprocessing, point counts |
| Figure 5 | overall performance | MRI, geospatial, graphics workloads; author `Running.AvgTime`; wall time; baseline context |
| Figure 6 | pruning effectiveness | Dragon-AsianDragon; No-Opt, EB, EB+Prune, RT-HDIST; intersections and visited pairs |
| Figure 7 | load balance | OSMLakes-OSMParks and graphics pairs; RT shader time and CUDA offload time |
| Figure 8 | radius-growing strategy | author script mapping and per-strategy timing |
| Figure 9 | adaptive grid sizing | grid configuration and timing |
| Figure 10 | scalability / overlap sensitivity | scale and overlap-controlled inputs |
| Figure 11 | memory footprint | GPU memory accounting boundary |

## Measurement Boundary

The matrix repeats the paper boundary because this is where unfair comparisons
usually start:

- Author `Running.AvgTime` / `ReportedTime` is an internal algorithm timing.
- Process wall time is separate.
- RTDL setup/preprocess/load/route/comparator phases are separate.
- No author-vs-RTDL ratio is allowed unless dataset, hardware, denominator, and
  timing regime align.

## What This Does Not Claim

- It does not claim exact paper dataset reproduction.
- It does not claim any Figure 5-11 reproduction.
- It does not claim author performance parity.
- It does not claim RTDL implements the X-HD RT algorithmic route.

## Next

Goal5131 should decide which dataset families are exact, same-source
representative, or blocked. The likely first real Level B gate is a graphics
pair from the Stanford 3D Scanning Repository, because it avoids BraTS license
friction and is smaller than the OSM-scale geospatial inputs.
