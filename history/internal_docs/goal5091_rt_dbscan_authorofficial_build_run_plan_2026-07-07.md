# Goal5091 RT-DBSCAN AuthorOfficial Build/Run Plan

Date: 2026-07-07

## Verdict Label

```text
completed_rt_dbscan_authorofficial_build_run_plan
```

## Purpose

Goal5091 prepares the next AuthorOfficial step for the RT-DBSCAN paper app.

Goal5090 located the candidate author artifact and created a local RTDL
core-count smoke gate. Goal5091 inspects the author sample interface and
decides what must be built or patched before a real same-input comparator can
exist.

This goal is a plan/runbook goal. It does not build the author artifact.

## Candidate Author Artifact

```text
repository: https://github.com/vani-nag/OWLRayTracing
branch: rt-dbscan
commit: 92749fe82ed001e5b7303265d4a2a73aa1bbf529
sample path: samples/cmdline/s02-rtdbscan
target: sample02-rtdbscan
```

GitHub tree inspection shows:

```text
samples/cmdline/s02-rtdbscan/ReadMe.md
samples/cmdline/s02-rtdbscan/CMakeLists.txt
samples/cmdline/s02-rtdbscan/hostCode.cpp
samples/cmdline/s02-rtdbscan/deviceCode.cu
samples/cmdline/s02-rtdbscan/deviceCode.h
```

## Author Sample Interface

The author sample README states:

```text
cd build
make sample02-rtdbscan
./sample02-rtdbscan [inFile] [size] [eps] [minPts] [outFile]
```

where:

```text
inFile  = input filename
size    = dataset size used for clustering
eps     = epsilon radius
minPts  = minimum points required for a cluster
outFile = file to write execution times
```

The CMake target is:

```text
sample02-rtdbscan
```

## Comparator Problem

Inspection of `hostCode.cpp` shows:

- the program reads a CSV-like input file,
- the dimensionality is currently hardcoded as `dim = 3`,
- it performs two launches:
  - call 1: core point identification,
  - call 2: cluster formation,
- it writes execution time to `outFile`,
- cluster result output is present in source but commented out.

Therefore the unmodified author binary is not yet a sufficient correctness
comparator for RTDL output. It provides timing output, but not an enabled
cluster/core output stream.

## Required AuthorOfficial Patch Strategy

Before same-input correctness can be claimed, the project needs a minimal
AuthorOfficial patch that emits one of:

1. `core_count` only,
2. per-point core flags,
3. cluster labels / component signature.

Recommended first comparator:

```text
core_count
```

Reason:

- it matches the Goal5090 first bounded RTDL target,
- it is an exact integer summary,
- it avoids committing too early to full cluster-label ordering,
- it exercises the paper-relevant core point identification phase.

Recommended second comparator:

```text
component signature
```

Only after the core-count gate passes.

## Proposed POD Build Plan

On a CUDA/OptiX-capable POD:

```text
git clone https://github.com/vani-nag/OWLRayTracing.git author/OWLRayTracing
cd author/OWLRayTracing
git checkout 92749fe82ed001e5b7303265d4a2a73aa1bbf529
mkdir -p build
cd build
cmake ..
make sample02-rtdbscan
```

Environment requirements from the repository README:

```text
OptiX 7.0 / 7.1 / 7.2 class SDK
CUDA 10 or 11 class toolchain
C++11 compiler
OWL build configured through CMake
```

Modern PODs may require compatibility patches, as happened for the
RT-BarnesHut app. Such patches must be documented as AuthorOfficial
compatibility patches, not silently treated as original author behavior.

## Proposed Same-Input Run Shape

Use a tiny generated 3D input first:

```text
./sample02-rtdbscan tiny.csv 8 0.35 3 timing.txt
```

RTDL side:

```text
py Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py
```

The author side must emit a `core_count` or core flags before comparison is
possible.

## Current Local Smoke Evidence

Goal5090 local smoke:

```text
backend: cpu_python_reference
point_count: 8
core_count: 7
oracle_core_count: 7
matches_oracle: true
author_comparator_used: false
```

Result artifact:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/core_count_smoke_summary.json
```

## Claim Boundary

This goal does not claim:

- author artifact build success,
- author comparator success,
- paper input recovery,
- RT-DBSCAN paper reproduction,
- performance comparison,
- native DBSCAN RTDL ABI,
- full cluster-label parity.

## Next Recommended Goal

Goal5092 should create a POD-ready AuthorOfficial patch/run packet:

1. generate the tiny 3D input fixture,
2. patch author `hostCode.cpp` to emit `core_count`,
3. build `sample02-rtdbscan`,
4. run same input on author and RTDL,
5. compare integer `core_count`,
6. record all compatibility patches and non-claims.
