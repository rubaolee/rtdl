# Goal3293 Direct CDB Segment Columns

Date: 2026-06-04

Status: complete with RTX A5000 before/after pod evidence.

## Purpose

Goal3290 and Goal3292 made segment packing faster after Python segment records
already exist. The next bottleneck is earlier: external RayJoin-style CDB chains
were converted into Python segment records, and then the prepared OptiX route
rebuilt those records into generic segment columns before packing.

This goal adds a direct CDB-to-segment-column path so the optimized LSI prepared
routes can start from generic column arrays instead of object/dict records.

## Implementation

- Added `rtdsl.datasets.chains_to_segment_columns(dataset, limit_chains=None)`.
- The converter builds `SegmentColumns2D` arrays directly from consecutive CDB
  chain points, preserving the same caller ids and endpoint geometry as
  `chains_to_segments(...)`.
- Exported `rt.chains_to_segment_columns(...)` from the public Python facade.
- Updated the external CDB LSI loader to accept `segment_column_inputs=True`.
- Updated prepared RayJoin LSI routes to request direct column inputs for
  external CDB datasets.
- Kept the CPU reference route unchanged. CPU reference route still uses ordinary segment records, which protects same-contract validation.

## Boundary

No native ABI changed. The native OptiX/Embree engine still sees generic segment
columns and packed segment buffers; RayJoin-specific meaning, workload names,
and comparison policy remain in Python/example code.

Claim flags:

- release_authorized: false
- public_speedup_claim_authorized: false
- rtdl_beats_rayjoin_claim_authorized: false
- full_rayjoin_reproduction_claim_authorized: false

## Local Validation

The regression test checks that the new CDB columns:

- have the same count as `chains_to_segments(...)`;
- preserve first/last ids and endpoint geometry;
- pack to the same native segment ids as the record path;
- are selected only by the optimized external LSI prepared routes;
- do not introduce app-specific native symbols.

A local Windows sanity probe on a synthetic tiled CDB-shaped fixture with 20,300
segments measured the old full input route (`chains_to_segments(...)` plus
`segments_from_records(...)`) at 66.391 ms median versus
`chains_to_segment_columns(...)` at 18.253 ms median. This is not pod evidence
and does not authorize a public speedup claim; it only confirms that the
loader-side optimization is worth the RTX same-slice retest.

## Pod Boundary

Pod timing was collected on an NVIDIA RTX A5000 pod with driver 580.126.09.
The pod checkout compared:

- before Goal3293: `5de3bc2655df6946e3c210aa4e4d06327e49a417`
- after Goal3293: `651dd8c49a4d4325ab18cc953581a9d3f400031d`

The test used the same generated public CDB slices as the Goal3290 same-slice
lane:

- LSI: `br_county_start256_count512.cdb + br_soil_start256_count512.cdb`
- PIP: `br_county_start0_count512.cdb`

Artifacts:

- `docs/reports/goal3293_previous_5de3bc26_rtdl_same_slice_pod_2026-06-04.json`
- `docs/reports/goal3293_current_651dd8c4_rtdl_same_slice_pod_2026-06-04.json`
- `docs/reports/goal3293_before_after_rtdl_same_slice_pod_2026-06-04.json`
- `docs/reports/goal3293_rayjoin_same_slice_current_pod_2026-06-04.json`

Median timings, warmup 3 and repeat 15:

| workload | metric | before Goal3293 | after Goal3293 | speedup |
| --- | ---: | ---: | ---: | ---: |
| LSI | query pack | 21.214 ms | 0.230 ms | 92.3x |
| LSI | static segment pack | 7.172 ms | 0.110 ms | 65.5x |
| LSI | prepared query | 0.382 ms | 0.331 ms | 1.15x |
| PIP | query pack | 0.600 ms | 0.451 ms | 1.33x |
| PIP | static shape pack | 15.216 ms | 12.329 ms | 1.23x |
| PIP | prepared query | 0.688 ms | 0.638 ms | 1.08x |

Counts stayed stable:

- LSI: 269 before and after.
- PIP: 1430 before and after.

This closes the loader/packing regression targeted by Goal3293. It does not
authorize a RayJoin-paper reproduction claim or an RTDL-beats-RayJoin claim,
because this before/after packet compares RTDL commits on the same pod and does
not rebuild/run the RayJoin C++ baseline on this pod.

## Same-Slice RayJoin Baseline

After the before/after RTDL packet, the same RTX A5000 pod rebuilt upstream
RayJoin `query_exec` and compared it with the current RTDL prepared OptiX count
route on the same generated CDB slices. RayJoin commit provenance is captured
inside `docs/reports/goal3293_rayjoin_same_slice_current_pod_2026-06-04.json`.

This packet has status `pass_with_optimization_gap`: RTDL preserves the visible
LSI count contract, but it still trails upstream RayJoin query timing on these
small same-slice runs.

| workload | RayJoin query reported median | RTDL prepared query median | RTDL / RayJoin | count contract |
| --- | ---: | ---: | ---: | --- |
| LSI | 0.233 ms | 0.362 ms | 1.55x | matching visible count, 269 |
| PIP | 0.221 ms | 0.666 ms | 3.01x | RayJoin PIP positive assignment count not exposed by the unpatched binary |

Interpretation:

- Goal3293 removed the largest RTDL-side loader/packing regression for external
  CDB LSI: direct CDB segment columns cut LSI query packing from 21.214 ms to
  0.230 ms and static segment packing from 7.172 ms to 0.110 ms.
- Against upstream RayJoin `query_exec`, the remaining gap is now in the
  prepared query/count path and in PIP device-side count/timing behavior, not in
  the old Python object-segment materialization path.
- The RayJoin PIP runner does not expose a positive assignment count in this
  unpatched build, so the PIP comparison is timing-only plus RTDL self-count
  reporting, not a full same-count contract.
- No release, public speedup, paper-reproduction, RT-core speedup, RTDL-beats-
  RayJoin, or true-zero-copy claim is authorized by this packet.
