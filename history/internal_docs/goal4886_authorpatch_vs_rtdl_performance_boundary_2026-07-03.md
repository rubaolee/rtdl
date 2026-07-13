# Goal4886 AuthorPatch vs RTDL Performance Boundary

Date: 2026-07-03

## Purpose

Record the honest performance boundary for the RayJoin Section 5.7 Australia
representative workload after adding the first Numba partner pass.

This document separates:

1. one-shot end-to-end time;
2. RayJoin query plus output time after excluding map read/build preparation;
3. RayJoin core compute time after also excluding output file writing.

The goal is to prevent a misleading claim such as:

> RTDL+Numba is faster than the author C++/CUDA/OptiX RayJoin kernel.

That claim is not supported. What is supported is narrower:

> On this representative workload, RTDL+Python+Numba is faster in one-shot
> end-to-end elapsed time, while the author patched C++/CUDA/OptiX route is
> still much faster in the hot RayJoin query/core phases.

## Comparator

The author comparator here means the patched author program used by the
RayJoin reproduction line:

```text
AuthorPatch / AuthorOfficial = author source + RTDLContractPatch
```

This is the agreed comparator for the current reproduction engineering line.

## Measured Inputs

RTDL current repeat:

```text
history/internal_docs/goal4886_pod_current_au_repeat_summary.json
elapsed: 117.258076146245 s
```

RTDL+Numba explicit skip-decision v2:

```text
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
elapsed: 103.78645047545433 s
byte_equal_to_author: true
```

AuthorPatch logged phases from the final comparator log:

```text
Read map 0:              134.688 s
Read map 1:                9.574 s
Load Data:                 3.801 s
Build Index:               0.032 s
Intersection edges:        0.00495 s
Map 0 locate vertices:     0.0211 s
Map 1 locate vertices:     0.00739 s
Compute output polygons:   0.00866 s
Write to file:             0.802 s
```

The final comparator log does not have a valid `/usr/bin/time` wall-time row.
The logged phase sum is therefore used only as a phase-sum comparison, not as a
separate wall-clock rerun.

## Three Performance Views

| View | AuthorPatch C++/CUDA/OptiX | RTDL+Python | RTDL+Python+Numba v2 | Honest conclusion |
| --- | ---: | ---: | ---: | --- |
| One-shot end-to-end, including read/build/output | `148.939 s` logged phase sum | `117.258 s` | `103.786 s` | RTDL+Numba is `1.435x` faster on this one-shot representative run. |
| Query + output, excluding read/build preparation | `0.844 s` | `36.076 s` | `20.920 s` | AuthorPatch is `24.78x` faster than RTDL+Numba in query+output phase-sum. |
| Core query compute, excluding read/build and output writing | `0.0421 s` | `19.550 s` | `18.880 s` | AuthorPatch is `448.47x` faster than RTDL+Numba in core phase-sum. |

## Phase Definitions

AuthorPatch one-shot end-to-end:

```text
Read map0 + Read map1 + Load Data + Build Index
+ Intersection edges + Map0 locate + Map1 locate
+ Compute output polygons + Write file
= 148.9391 s
```

AuthorPatch query + output:

```text
Intersection edges + Map0 locate + Map1 locate
+ Compute output polygons + Write file
= 0.8441 s
```

AuthorPatch core query compute:

```text
Intersection edges + Map0 locate + Map1 locate
+ Compute output polygons
= 0.0421 s
```

RTDL current query + output:

```text
lsi_public_rows
+ intersection_reprojection
+ sort_map0 + sort_map1
+ vertex_pip_map0_in_map1 + vertex_pip_map1_in_map0
+ midpoint_pip_map0 + midpoint_pip_map1
+ output_chain_write
= 36.0756 s
```

RTDL+Numba v2 query + output:

```text
lsi_public_rows
+ intersection_reprojection
+ sort_map0 + sort_map1
+ vertex_pip_map0_in_map1 + vertex_pip_map1_in_map0
+ midpoint_pip_map0 + midpoint_pip_map1
+ output_chain_write
= 20.9200 s
```

RTDL+Numba v2 core query compute:

```text
RTDL+Numba v2 query + output - output_chain_write
= 18.8805 s
```

## Why The Gap Is Large

The author route and RTDL route are currently doing the same reproduction task
through very different execution structures.

The author C++/CUDA/OptiX route has:

- native C++ data structures after map loading;
- no Python interpreter in the query loop;
- direct CUDA/OptiX kernels for the RayJoin stages;
- fused or tightly coupled overlay logic;
- little per-stage host materialization in the reported query phases;
- direct output construction in the same native application.

The current RTDL public-primitives route has:

- Python-level orchestration between public RTDL primitives;
- public LSI and PIP primitive calls that return rows back to the Python app;
- Python sorting, reprojection, face assembly, and output-chain logic;
- separate primitive boundaries rather than a fused overlay pipeline;
- text/CDB load-pack work that is not yet a reusable prepared dataset cache;
- Numba acceleration only for selected application-layer continuation decisions,
  not for RTDL LSI/PIP traversal.

This is why the one-shot end-to-end number can look favorable while the hot
RayJoin phase remains far behind: the author path pays a very large map read
cost on this representative run, while its already-prepared query machinery is
extremely fast. RTDL currently benefits from a more favorable one-shot balance
on this dataset, but it does not yet match the author's fused hot-path design.

## What Numba Actually Improved

Numba did not accelerate RTDL LSI or PIP.

Numba accelerated the application-layer writer/continuation path:

```text
Current RTDL output-chain write:       16.525 s
RTDL+Numba explicit skip-decision v2:   2.040 s
writer-phase speedup:                  8.10x
```

The skip plan avoided Python per-point writer work for:

```text
skipped_no_xsect_chains: 399419
skipped_no_xsect_points: 14996199
processed_chains: 9621
```

This is real partner value, but it is not a core RT traversal win.

## Why The Next Work Must Target Prepared/Cache And Fused Continuation

The phase breakdown points to the next work. It should not be chosen by taste.

1. Prepared/cache work is needed because load/pack is still dominant in the
   one-shot RTDL route:

   ```text
   RTDL+Numba v2 load_pack_left + load_pack_right
   = 72.279 + 4.772
   = 77.051 s
   ```

   If the user repeats queries over the same maps, this cost should not be paid
   every time. A prepared CDB/map cache is the right systems-level optimization.

2. Fused continuation work is needed because even after removing load/pack and
   output writing, the RTDL query/core phase is still about `18.88 s` while the
   author core phase is about `0.042 s`.

   That gap is not caused by string output. It comes from separated primitive
   boundaries, Python orchestration, row materialization, and unfused overlay
   assembly. The only plausible path toward the author hot-path shape is to
   keep more continuation work near the RTDL primitive outputs and reduce
   host/Python round trips.

3. Numba remains useful, but only where it moves measured app-layer work.
   The successful writer-skip result shows that partner acceleration works when
   aimed at a real bottleneck. It does not justify claiming that every Python
   helper should be JITed.

## Allowed Claim

Allowed:

```text
On the Australia representative Section 5.7 route, RTDL public primitives plus
Numba preserve byte-equal correctness and improve one-shot RTDL elapsed time
from 117.258 s to 103.786 s in the clearer explicit-skip implementation.
The improvement comes from app-layer writer/continuation acceleration.
```

Also allowed:

```text
Compared with the patched author program's logged phase sum, this one-shot
representative RTDL+Numba run is faster end-to-end.
```

## Forbidden Claim

Forbidden:

```text
RTDL+Numba has a faster RayJoin kernel/hot path than the author C++/CUDA/OptiX
program.
```

Forbidden:

```text
RTDL+Numba is broadly faster than RayJoin across Section 5.7.
```

Forbidden:

```text
Numba accelerated RTDL LSI/PIP primitives.
```

Those statements are not supported by the current evidence.
