# Goal2521 RayDB Authors-Code Feasibility Gate

Date: 2026-05-23

## Verdict

Do not run or claim a performance comparison against the RayDB authors code yet.

The authors artifact is available and useful as a design/reference source, but
Goal2521 blocks immediate timing and blocks same-contract performance
comparison. The current evidence supports this status:

- authors code available: yes;
- authors code built: no;
- authors code timed: no;
- same-contract comparison authorized: no;
- public speedup claim authorized: no;
- source copied into RTDL: no.

The correct next step is not "benchmark now". The next possible step is a
separate build-only reproduction goal after accepting the pod/toolchain/data
cost, or a same-contract adapter design goal if we want a fair subpath
comparison.

## Sources Rechecked

Authors artifact:

- repository: `https://github.com/LonelySlim/myOptixDB.git`
- branch: `fin`
- current branch head from `git ls-remote`:
  `a610c00d7334d8907435cc0a124f9ca8392ee456`
- local inspection clone: `/tmp/rtdl_goal2521_myOptixDB`
- clone purpose: inspection only
- third-party source copied into RTDL: no

The branch head matches the earlier Goal2493 intake result.

Local inspected commit:

```text
a610c00d7334d8907435cc0a124f9ca8392ee456
2024-11-06 18:47:36 +0800
v0.5
```

## Artifact Shape

The inspected repository contains:

- `README.md`
- `Makefile`
- bundled OptiX 7 headers under `include/`
- RayDB source under `src/raydb/`
- NVIDIA sample-style support code under `src/sutil/`
- query preprocessors under `ssb_data/q*/`
- `script/data_preprocess.sh`
- `script/run.py`

The generated SSB CSV and binary data files are not included. The repository
contains predicate files and preprocessor source files, not the generated
`file_*.csv` / `data.txt` payloads required by the run script.

## Build Gate

The authors README records this tested environment:

- NVCC 12.2.140
- CMake 3.16.3
- GCC/G++ 8.4.0
- OptiX 7.1, bundled in the project
- RTX-capable NVIDIA GPU, tested on RTX 4090

The Makefile hard-codes:

```text
CMAKE_C_COMPILER=/usr/bin/gcc-8
```

Our recent RTDL pod work used a different OptiX branch and driver environment:
OptiX 8.0 through `optix-dev`, CUDA 12.8 runtime libraries, and driver
compatibility handling. That does not make authors-code build impossible, but
it means build reproduction is a dedicated environment task, not a free
extension of the current RTDL pod setup.

Build status for Goal2521:

```text
blocked_without_dedicated_pod_and_legacy_toolchain
```

## Data Gate

The authors README requires:

1. clone and build `ssb-dbgen`;
2. generate SSB tables at scale factor 20;
3. import tables into a database such as MonetDB;
4. denormalize to `lineorder_flat`;
5. export query-specific CSV files into `ssb_data/q*/file_*.csv`;
6. run `script/data_preprocess.sh`;
7. run `python script/run.py`.

The run script hard-codes `dataset_size = 119994608` for its SSB query suite.

Data status for Goal2521:

```text
blocked_generated_ssb_sf20_data_not_present
```

## License Gate

The quick inspection found no repo-level `LICENSE`, `COPYING`, or `NOTICE`
file. Many NVIDIA sample/support files carry NVIDIA sample-style BSD headers,
but that does not establish the license status of the full RayDB artifact.

License status for Goal2521:

```text
unresolved_no_repo_level_license_file
```

This blocks copying or vendoring authors code into RTDL. Inspection and
external build attempts remain acceptable if we keep the code outside this repo.

## Same-Contract Gate

Our closed RayDB-style RTDL app is a synthetic contract harness:

- tiny denormalized fixture;
- integer-coded columns;
- one grouped key in the partner-resident native path;
- grouped `count`, `sum`, `min`, `max`, and `avg_as_sum_count`;
- explicit dense `group_capacity`;
- compact grouped result materialization;
- CPU oracle in Python;
- app-neutral runtime dispatcher for generic grouped i64 reductions.

The authors artifact targets full SSB query scripts:

- SF=20 scale assumptions;
- query-specific CSV extraction from `lineorder_flat`;
- query-specific binary preprocessing;
- hard-coded query dimensions and predicate files;
- full RayDB OptiX kernel path;
- no exposed tiny fixture matching our current app;
- no exposed CPU oracle matching our current result modes.

Same-contract requirements before any fair comparison:

- same input rows and columns;
- same predicates;
- same grouping keys;
- same aggregate result modes;
- same result materialization boundary;
- same correctness oracle.

Current same-contract status:

| Requirement | Status |
| --- | --- |
| Same input fixture | Not satisfied |
| Same predicates | Not satisfied |
| Same grouping keys | Not satisfied |
| Same aggregate modes | Not satisfied |
| Same result materialization boundary | Not satisfied |
| Same correctness oracle | Not satisfied |

Same-contract status for Goal2521:

```text
blocked_not_same_contract_yet
```

## Decision Matrix

| Gate | Result | Effect |
| --- | --- | --- |
| Authors repo availability | Pass | Code can be inspected outside RTDL |
| Branch identity | Pass | `fin` currently resolves to `a610c00d...` |
| Build readiness | Blocked | Needs dedicated pod/toolchain work |
| Data readiness | Blocked | Needs SSB SF=20 generation/export/preprocess |
| License clarity | Blocked for vendoring | No repo-level license file found |
| Same-contract comparison | Blocked | Current RTDL app and authors code do not expose the same benchmark contract |
| Performance comparison | Blocked | No timing is valid until build/data/same-contract gates pass |

## What We Can Say Now

Allowed:

- RayDB authors code is available at the inspected GitHub repository/branch.
- It is useful as a design reference for fused scan/group/aggregate over
  ray-tracing primitives.
- It is not currently a valid performance baseline for our synthetic
  RayDB-style RTDL app.

Blocked:

- "RTDL is faster/slower than RayDB";
- authors-code timing;
- public speedup wording;
- whole-app comparison;
- SQL/DBMS claim;
- RayDB reproduction claim;
- copying/vendoring authors code into RTDL;
- comparing Goal2518 fused `sum_count` timing against authors RayDB.

## Recommended Next Goals

If the user wants authors-code performance evidence:

1. `Goal2522`: build-only reproduction attempt on a dedicated pod. This goal
   should install/probe GCC 8, CUDA/NVCC compatibility, CMake, and OptiX 7.1
   expectations, then record whether `build/bin/raydb` can be produced.
2. `Goal2523`: data-pipeline reproduction gate. This goal should decide
   whether SSB SF=20 data generation, MonetDB import/export, and preprocessing
   are worth the cost.
3. `Goal2524`: same-contract adapter design. This goal should decide whether
   to adapt authors code to a tiny fixture or adapt RTDL to one authors query
   subpath without changing native RTDL into a DBMS.
4. `Goal2525`: performance comparison only if the previous gates pass.

If the user only wants RTDL language/runtime reconstruction, stop here and move
to the next benchmark app or next RTDL primitive gap.
