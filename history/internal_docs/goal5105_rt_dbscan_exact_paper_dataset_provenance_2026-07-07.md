# Goal5105 - RT-DBSCAN Exact Paper Dataset Provenance Audit

Date: 2026-07-07

## Verdict

```text
exact_paper_inputs_not_pinned__candidate_sources_recorded
```

Goal5105 pursued the exact RT-DBSCAN paper dataset provenance path. The outcome
is useful but bounded:

- The paper's four datasets are identified: `3DRoad`, `NGSIM`, `Porto`, and
  `3DIono`.
- Public source candidates are identified for `3DRoad`, `Porto`, and `NGSIM`.
- The pinned author artifact contains developer-local filename hints for
  `3D_iono.txt`, `porto.txt`, and `3droad_full.csv`.
- The exact preprocessed paper input files are not packaged in the author
  repository and are not present in the RTDL paper app.
- Therefore exact RT-DBSCAN paper dataset reproduction is still not closed.

This result is recorded in
`Paper-reproduction-apps/rt-dbscan-paper/data/paper_dataset_candidates.json`.

## Local Evidence

The pinned AuthorOfficial artifact remains:

```text
repository: https://github.com/vani-nag/OWLRayTracing
branch: rt-dbscan
commit: 92749fe82ed001e5b7303265d4a2a73aa1bbf529
sample path: samples/cmdline/s02-rtdbscan
```

The sample README says the program is invoked as:

```text
./sample02-rtdbscan [inFile] [size] [eps] [minPts] [outFile]
```

The source reads `av[1]` as the input file. It does not select a built-in paper
dataset. The same source file contains three commented developer-local paths:

```text
/home/min/a/nagara16/fast-cuda-gpu-dbscan/CUDA_DCLUST_datasets/3D_iono.txt
/home/min/a/nagara16/ArborX/build/examples/dbscan/porto.txt
/home/min/a/nagara16/Downloads/owl/samples/cmdline/s01-simpleTriangles/testing/3droad_full.csv
```

No matching `3D_iono.txt`, `porto.txt`, `3droad_full.csv`, or NGSIM file is
packaged in the pinned repository checkout. The current RTDL paper app contains
only bounded and representative synthetic fixtures.

Important implementation detail: the pinned `hostCode.cpp` has `int dim = 3`.
The paper says 2D data are handled by setting z to 0, but the checked source
does not expose a runtime 2D mode. This strongly suggests that the paper inputs
used by the sample were preprocessed into the author program's expected numeric
point stream, not consumed directly from raw public source files.

## Paper Evidence

Primary paper source:

- [RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware](https://par.nsf.gov/servlets/purl/10467236)

The paper states in Section V-A that it evaluates four real-world datasets:

- `3DRoad`: North Jutland road-network data, 435K points, used as 2D latitude
  and longitude.
- `NGSIM`: vehicle trajectories, more than 11M points, using local coordinates
  as 2D input.
- `Porto`: taxi trajectory data from Porto, using 2D GPS coordinates.
- `3DIono`: ionosphere data, using latitude, longitude, and total electron
  count as 3D input.

The paper also gives workload policy:

- Impact-of-epsilon: first 1M points, `minPts=100`, varying epsilon.
- Dataset-size study: first `n` points.
- Dataset-size fixed parameters: `(epsilon,minPts) = (0.05,100)` for 3DRoad,
  `(0.5,10)` for 3DIono, and `(0.5,1000)` for Porto.
- NGSIM dense study: `minPts=100`; tables report varying epsilon and sizes.

Public source candidates found:

- [UCI 3D Road Network (North Jutland, Denmark)](https://archive.ics.uci.edu/dataset/246/3d+road+network+north+jutland+denmark)
  lists 434,874 instances and variables `OSM_ID`, `LONGITUDE`, `LATITUDE`, and
  `ALTITUDE`.
- [UCI Taxi Service Trajectory - Prediction Challenge, ECML PKDD 2015](https://archive.ics.uci.edu/dataset/339/taxi+service+trajectory+prediction+challenge+ecml+pkdd+2015)
  lists 1,710,671 trip records with `POLYLINE` GPS coordinate lists.
- [U.S. DOT NGSIM Vehicle Trajectories and Supporting Data](https://data.transportation.gov/Automobiles/Next-Generation-Simulation-NGSIM-Vehicle-Trajector/8ect-6jqj)
  is the paper's NGSIM public source candidate.
- [NOAA/NCEI Total Electron Content products](https://www.ncei.noaa.gov/products/space-weather/ionospheric-program/total-electron-content)
  are public TEC source candidates, but they do not identify the exact processed
  `3D_iono.txt` used by the author sample.

## Dataset Status

| Dataset | Candidate source | Author hint | Exact status |
| --- | --- | --- | --- |
| 3DRoad | UCI 3D Road Network | `3droad_full.csv` | Public source identified; exact preprocessed author file not present |
| Porto | UCI Taxi Service Trajectory Challenge | `porto.txt` | Public source identified; author point extraction from polylines not present |
| 3DIono | paper reference plus public TEC sources | `3D_iono.txt` | Author-local filename identified; exact public processed file not pinned |
| NGSIM | U.S. DOT NGSIM trajectories | no local source hint found | Public source identified; site/coordinate extraction not pinned |

## Why This Is Not Exact Yet

Exact paper dataset reproduction requires more than dataset names:

1. The exact raw input source must be pinned by URL, version, and hash.
2. The exact preprocessing from raw source to the author's numeric point stream
   must be reproducible.
3. The exact coordinate columns, unit scaling, z-column policy, point ordering,
   and prefix selection must be pinned.
4. The exact `(size, epsilon, minPts)` workload rows must be run through the
   same patched AuthorOfficial comparator and RTDL route.

None of those are fully satisfied yet for any one full paper workload.

The current synthetic fixtures remain valuable bounded tests, but they are not
paper datasets.

## Authorized Claims

Allowed:

```text
RT-DBSCAN paper dataset provenance candidates have been identified and recorded.
The exact preprocessed paper input files remain unpinned.
The current RTDL paper app remains a bounded same-input and representative
synthetic reproduction line, not a full paper dataset reproduction.
```

Not authorized:

```text
exact RT-DBSCAN paper dataset reproduction
full RT-DBSCAN paper reproduction
paper-performance reproduction
author-performance parity
RTDL speedup on paper datasets
```

## Recommended Next Goal

Goal5106 should choose one of two routes:

1. **Exact-first route:** acquire or reconstruct one exact paper workload input
   end to end, preferably 3DRoad because its public source size closely matches
   the paper's 435K statement and the UCI source is directly accessible. This
   still requires pinning the author-compatible three-column transformation and
   hash before any run can be called exact.
2. **Same-source public route:** if exact author-preprocessed inputs cannot be
   obtained, explicitly define a non-exact public-source reproduction route,
   such as "UCI 3DRoad same-source, RTDL transformation," and label it
   representative/same-source rather than exact.

The second route is acceptable engineering, but it must not be sold as exact
paper reproduction.
