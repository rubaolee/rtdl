# Goal2493: RayDB Local/External Code Intake

Date: 2026-05-22

## Status

Goal2493 completes the first RayDB intake pass for the post-robot-collision
benchmark-app campaign.

Decision: RayDB authors code is available and useful as design reference, but
it should not be the immediate RTDL benchmark baseline. The next RTDL step
should be a synthetic database-shaped fixture and contract design, not a full
authors-code reproduction.

## Sources Checked

Local repo:

- `rg` and scoped `find` found no RayDB implementation inside
  `/Users/rl2025/rtdl_python_only` beyond historical reports and the new
  Goal2492/Goal2493 docs.
- Existing local work already covers related but different lanes:
  `spatial_rayjoin`, `database_analytics`, RTScan/RayDB historical reports, and
  partner-column database reductions.

External paper/source anchors:

- The RayDB paper PDF says the artifact is available at
  `https://github.com/LonelySlim/myOptixDB/tree/fin`.
- GitHub branch check:
  `git ls-remote --heads https://github.com/LonelySlim/myOptixDB.git fin`
  returned commit `a610c00d7334d8907435cc0a124f9ca8392ee456`.
- A lightweight clone was made outside the repo at
  `/tmp/rtdl_goal2493_myOptixDB` for inspection only. No third-party source was
  copied into RTDL.

Source links:

- RayDB PDF: `https://kay21s.github.io/RayDB-VLDB26.pdf`
- Artifact repo: `https://github.com/LonelySlim/myOptixDB/tree/fin`

## External Repo Snapshot

Inspected branch:

```text
repo: https://github.com/LonelySlim/myOptixDB.git
branch: fin
commit: a610c00d7334d8907435cc0a124f9ca8392ee456
last commit date: 2024-11-06 18:47:36 +0800
last commit subject: v0.5
```

Top-level shape:

- `README.md`
- `Makefile`
- `include/` with OptiX 7 headers
- `src/raydb/` with `raydb.cpp`, `raydb.cu`, `raydb.h`, `group.h`, `timer.h`
- `ssb_data/` with per-query preprocessors and predicate files
- `script/data_preprocess.sh`
- `script/run.py`

The clone size is small (`1.3M`) because generated SSB data files are not
included.

## Build And Data Requirements

The external README states these tested requirements:

- NVCC 12.2.140
- CMake 3.16.3
- GCC/G++ 8.4.0
- OptiX 7.1, included in the project
- RTX-capable NVIDIA GPU, tested on RTX 4090

The data path requires:

- cloning and building `https://github.com/vadimtk/ssb-dbgen.git`;
- generating SSB tables at scale factor 20;
- loading the generated tables into a database such as MonetDB;
- denormalizing the tables into a single `lineorder_flat` table;
- exporting query-specific CSV files into `ssb_data/q*/file_*.csv`;
- running `script/data_preprocess.sh` to produce binary `data.txt` files;
- running `python script/run.py`.

The run script hard-codes `dataset_size = 119994608` for the SSB SF=20 query
suite. That makes the artifact valuable but too heavy and too environment-bound
for immediate local RTDL iteration.

## Code-Level Observations

The artifact appears to implement a fused RayDB query kernel:

- data records are read from binary columns into average, group, and scan
  buffers;
- group columns are remapped to compact group IDs;
- scan predicates are merged into a scan coordinate;
- each record becomes a triangle in a 3D coordinate space;
- OptiX launches rays over a grid controlled by `interval_x`, `interval_y`, and
  predicate-origin data;
- the any-hit shader uses `atomicOr` to deduplicate primitive hits and
  `atomicAdd` into grouped result slots.

This is useful for RTDL because it confirms the reconstruction target:

- columnar query/data descriptors;
- prepared/offline BVH lifetime;
- fused scan/group/aggregate result modes;
- grouped result slots;
- explicit handling of atomics and duplicate hits.

It is not a clean immediate baseline because:

- the implementation is OptiX-only;
- it targets old OptiX/CUDA/GCC versions;
- it uses bundled OptiX headers rather than our current OptiX setup;
- it is tightly coupled to SSB data preprocessing and hard-coded query shapes;
- it has no simple small fixture or CPU oracle exposed by the repo;
- it has no repo-level `LICENSE`, `COPYING`, or `NOTICE` file found in the
  intake clone.

Several files contain NVIDIA sample-style BSD license comments, but that does
not by itself establish the license status of the full RayDB artifact. Treat
license as unresolved for copying or vendoring code.

## Decision

Do not use authors-code performance comparison as the next step.

Use the external artifact as design reference only until all of these are true:

- license status is clarified enough for the intended use;
- a pod/toolchain can support or adapt the old OptiX 7.1 / GCC 8.4 / CUDA 12.2
  build assumptions;
- SSB generation and MonetDB export cost are accepted;
- a same-contract output comparison against RTDL is defined.

The immediate RTDL path should be synthetic and contract-first:

```text
small denormalized table fixture
-> columnar RTDL descriptors for value, group, and predicate axes
-> CPU reference grouped scan/aggregate
-> Embree same-contract path where feasible
-> OptiX same-contract path when a pod is available
```

This respects the project rule: the app exists to force RTDL language/runtime
reconstruction, not to become a full RayDB clone.

## Implications For Goal2494

Goal2494 should design a generic contract shaped by RayDB but not named after
RayDB in native engines:

- `ColumnarRecordAxis`: app-level descriptor for an integer or float column
  projected into a geometry axis;
- `PredicateAxisRange`: app-level descriptor for range/equality filter
  intervals;
- `GroupSlotDescriptor`: stable grouping output slot mapping;
- `AggregateDescriptor`: count, sum, min, max, or average-as-sum/count pair;
- `PreparedColumnarScene`: prepared RT index over encoded records;
- `RayQueryGridDescriptor`: query rays/segments derived from predicate ranges;
- `GroupedAggregateResult`: scalar or vector result slots with duplicate-hit
  policy metadata.

Names above are Goal2494 design candidates, not committed API.

## Non-Claims

Goal2493 does not claim:

- RTDL reproduces RayDB;
- RTDL beats RayDB, Crystal, HeavyDB, MonetDB, or any authors baseline;
- authors-code was built or timed;
- SSB data was generated;
- external code can be copied into RTDL;
- a public RayDB performance claim is authorized;
- native Embree/OptiX should gain database, SQL, or RayDB-specific vocabulary.

## Next Step

Proceed to Goal2494: design the synthetic RayDB-style contract. The first
implementation target should be a tiny CPU reference fixture that expresses a
denormalized table, range predicates, grouping keys, and grouped aggregates in
Python, then lowers only the app-agnostic geometric part into RTDL.
