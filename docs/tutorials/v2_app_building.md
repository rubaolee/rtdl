# v2.0 App Building

This tutorial explains how to build a current RTDL program as a Python app with
an RTDL kernel boundary and optional partner-owned columns.

The rule is simple:

```text
Python app logic
  -> partner or Python arrays
  -> RTDL primitive contract
  -> backend traversal/refinement
  -> Python or partner continuation
```

The native engine stays app-agnostic. Your Python program can be about
Hausdorff distance, road screening, graph visibility, or database-style
summaries, but the engine should see generic traversal inputs and output
contracts.

## The Three Layers

| Layer | Owner | Typical work |
| --- | --- | --- |
| Python app | you | load data, choose scenario, call RTDL, compute final labels or reports |
| Partner framework | NumPy, PyTorch, or CuPy | hold columns, run array math, perform reductions where useful |
| RTDL | RTDL runtime and backend | traverse, refine, and emit documented primitive outputs |

In v2.0, the important upgrade is not that RTDL replaces Python or partner
frameworks. The upgrade is that RTDL can participate in a cleaner column-based
program where the RT-shaped part is a reusable runtime contract.

## Start With A Portable Program

Run from the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend embree
```

That program uses NumPy-owned columns, then calls RTDL through the partner
any-hit bridge. Embree is the CPU RT fallback, so this is the best first v2.0
developer path on a local Linux or Windows machine.

## Move To GPU Partner Columns

On a configured NVIDIA host with CuPy or PyTorch CUDA available, the same
programming idea can use GPU-owned input columns:

```bash
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend optix
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner torch-cuda --backend optix
```

For larger app-level examples, use the application catalog and the performance
reports linked from the v2.0 release package. Treat each measured row as
a specific contract: backend, partner, problem size, output shape, and hardware
all matter.

## Continuation Work

RTDL does not need to own every operation after traversal. A v2.0 program can
continue in normal Python, NumPy, PyTorch, or CuPy.

Examples:

- a segment/polygon program can ask RTDL for witness columns, then use CuPy to
  summarize the result;
- a Hausdorff-style program can ask RTDL for candidate rows, then use Python or
  partner reductions to choose the final witness;
- a graph program can ask RTDL for frontier/edge rows, then let Python own the
  outer iteration policy;
- a DB-style program can ask RTDL for bounded columnar-payload summaries, then
  use Python to format the application answer.

That split is intentional. It keeps RTDL general-purpose without putting
application-specific reducers inside the native engine.

## Reuse Prepared And Packed Inputs

For repeated calls, do not rebuild the same RTDL boundary objects each time.
Use this pattern:

1. prepare static build-side geometry once;
2. pack reusable probe/query geometry once;
3. run raw/count/reduction calls over the prepared and packed objects.

For a segment-pair workload on OptiX:

```python
from rtdsl.optix_runtime import pack_segments
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix

prepared_right = prepare_segment_pair_intersection_optix(right_segments)
packed_left = pack_segments(records=left_segments)

rows = prepared_right.run_raw(packed_left)
try:
    row_count = rows.row_count
finally:
    rows.close()

exact_count = prepared_right.count(packed_left)
```

The same idea applies broadly: prepared objects avoid rebuilding static scene
state, and packed objects avoid repacking Python records when the same batch is
used more than once.

Reviewed Goal2284/2285 evidence measured this effect on one RTX A5000
RayJoin-exported 100k LSI stream: repeated prepared segment-pair calls improved
by about `20x` when the left/query segments were prepacked instead of passed as
tuple records every time. That is a narrow measured contract, not a promise that
every workload gets a 20x gain.

## What To Avoid

Do not turn a Python app name into a native engine feature. Prefer generic RTDL
contracts such as:

- any-hit rows;
- count rows;
- closest-hit rows;
- fixed-radius rows;
- streaming witness columns;
- grouped numeric summaries;
- columnar-payload scan summaries.

Do not publish a speedup claim from a tutorial run. Use reviewed benchmark
artifacts and the exact claim boundary instead.

## Read Next

- [Python Partner Any-Hit](partner_anyhit.md)
- [OptiX Partner Column Any-Hit](partner_optix_zero_copy_anyhit.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)
- [Application Catalog](../application_catalog.md)
- [Current Architecture](../current_architecture.md)
