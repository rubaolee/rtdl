# Goal4400 V3.0 Local M1-M7 Progress And Pod Request

Date: 2026-06-15

Status: local V3.0 M1-M7 preparation complete through no-execution graph, instrumentation, pilot, and harness skeletons. Full measured M4-M7 remains blocked on pod access.

## Current Result

Local work completed in this session:

| Milestone | Status | Commit |
| --- | --- | --- |
| M1 execution-graph IR freeze | complete, 3-AI reviewed | `4bbfbfab` |
| M2 no-execution graph skeleton | complete | `0c090907` |
| M3 instrumentation metadata | complete locally | `31079f0b` |
| M4 component-union pilot local prep | complete locally | `7f9a9e36` |
| M5 topology pilot local prep | complete locally | `049fde02` |
| M6 frontier/vector pilot local prep | complete locally | `65038f0c` |
| M7 benchmark harness skeleton | complete locally | `bc577602` |

## Current Tests

Latest V3/governance suite:

```text
68 tests OK
```

Latest focused milestone stacks:

```text
M1-M3: 27 tests OK
M1-M4: 32 tests OK
M1-M5: 36 tests OK
M1-M6: 40 tests OK
M1-M7: 45 tests OK
```

## What Is Done

V3.0 now has:

- frozen M1 execution-graph IR design and consensus;
- app-agnostic public V3 metadata objects;
- no-execution `PreparedGraph` validation;
- claim-boundary validation;
- explicit partner-policy validation;
- stream/residency/lifetime/materialization metadata;
- M3 evidence metadata for CUDA events, Nsight correlation, pointer identity, transfer counters, no-host-materialization evidence, Embree timers, and CPU timers;
- local M4 graphs proving `continuation.component_union` reuse;
- local M5 graphs for generic topology stream and compaction;
- local M6 graphs for generic frontier/vector-sum reuse;
- local M7 benchmark harness row/packet validation.

## What Is Not Done

The following require a working pod:

- OptiX/RT-core execution evidence;
- Embree same-contract CPU evidence on the same run packet;
- CUDA event or Nsight evidence for same-stream claims;
- pointer or native-handle evidence for device-resident values;
- transfer-counter or no-host-stage evidence;
- measured M4-M7 phase tables;
- release-grade V3 public performance wording.

## Failed Access Attempts

These checks were attempted from the local workspace and failed with `Permission denied`:

```text
ssh -i ~/.ssh/id_ed25519 -p 22234 root@157.157.221.29
ssh -i ~/.ssh/id_ed25519 root@192.168.1.20
```

## Needed From User

Please provide one current SSH line for a running pod, for example:

```text
ssh root@HOST -p PORT -i ~/.ssh/id_ed25519
```

The pod should have:

- NVIDIA GPU with OptiX-capable driver;
- CUDA toolkit or enough runtime tools for CUDA event timing;
- repo access or enough network access to clone/pull `rubaolee/rtdl`;
- Python environment capable of running the current test suite;
- Embree dependencies or existing project setup scripts.

## First Pod Actions

Once pod access works:

1. pull latest `main`;
2. verify GPU and driver with `nvidia-smi`;
3. run the V3 M1-M7 tests on Linux;
4. build or verify OptiX/Embree native libraries;
5. run M3 evidence probes for CUDA events, pointer identity, transfer counters, and Embree phase timers;
6. run M4 component-union pilot measurements;
7. run M5 topology pilot measurements;
8. run M6 frontier/vector pilot measurements;
9. load rows into the M7 harness packet;
10. request external review before any public performance wording.

## Current Gate

Local V3 preparation is ahead of pod evidence. The next real unblocker is working SSH access.

Current state:

`v3_0_local_m1_m7_ready_pod_evidence_required`
