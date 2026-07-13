# Goal4868 Duplicate Half-Edge Core Contract Report

Date: 2026-07-02

## Scope

Goal4868 implements and tests a deterministic RTDL directed-segment point-location contract for duplicate half-edges:

- duplicate half-edges are grouped by unordered exact scaled endpoint pair;
- each group canonicalizes to the smallest stable source segment id;
- the emitted face id is computed from that canonical segment's direction;
- the canonical result is emitted by the OptiX kernel itself, so row output, device segment ids, device face ids, and positive-face count share one contract.

This is a product/core point-location contract repair. It is not a RayJoin output-chain patch.

## Files Changed

- `src/native/optix/rtdl_optix_core.cpp`
  - Added `canonical_segment_ids` and `canonical_face_ids` to the point-location launch params.
  - Changed `__raygen__rayjoin_cdb_point_location` to emit canonical segment/face ids.

- `src/native/optix/rtdl_optix_workloads.cpp`
  - Builds the duplicate-half-edge canonical table during `PreparedRayjoinCdbPointLocation2D` construction.
  - Uploads canonical segment/face tables to the GPU.
  - Passes canonical tables into the OptiX point-location launch params.

- `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
  - Updated the source-shape assertions from raw `segment.id` output to canonical segment/face output.

- `history/internal_docs/goal4867_duplicate_half_edge_micro_probe.py`
  - Already extended to report the candidate Goal4868 canonical segment id.

## Build And Focused Test Evidence

POD:

```text
ssh root@157.157.221.29 -p 23132 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
workspace: /workspace/rtdl_goal4859_exec
OptiX SDK: /tmp/optix-sdk-probe
```

Build command:

```bash
cd /workspace/rtdl_goal4859_exec
make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe
```

Result: build completed successfully.

Focused tests:

```bash
export PYTHONPATH=/workspace/rtdl_goal4859_exec/src:/workspace/rtdl_goal4859_exec/history/internal_docs
export LD_LIBRARY_PATH=/workspace/rtdl_goal4859_exec/build:${LD_LIBRARY_PATH:-}
python -m unittest \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4373_rayjoin_cdb_point_location_route_test
```

Result:

```text
Ran 20 tests in 1.410s
OK
```

## Micro Probe Evidence

Artifact:

`history/internal_docs/goal4868_duplicate_half_edge_micro_probe_after_core_canonical.json`

The probe uses two exact duplicate half-edge inputs differing only in input order:

| case | input segment ids | emitted segment id | emitted face id | canonical segment id | native matches canonical |
|---|---:|---:|---:|---:|---|
| forward_then_reverse | 100, 200 | 100 | 0 | 100 | true |
| reverse_then_forward | 200, 100 | 100 | 0 | 100 | true |

Before Goal4868, `reverse_then_forward` emitted segment `200` / face `22`. After Goal4868 it emits segment `100` / face `0`. This proves the native route no longer exposes duplicate half-edge input-order dependence for this controlled case.

## Block x Water Witness Probe

Artifact:

`history/internal_docs/goal4868_specific_pip_probe_after_core_canonical.json`

Dataset:

- left: `USACensusBlockGroupBoundaries_Point.cdb`
- right: `USADetailedWaterBodies_Point.cdb`
- query map id: `0`
- cached input load: `1.037s`
- prepare: `11.167s`
- run: `0.00054s`

Witness results:

| point index | point text | emitted face id | emitted segment id | interpretation |
|---:|---|---:|---:|---|
| 1069665 | `-88.157424 30.463452` | 323443 | 15220835 | unchanged expected witness |
| 5693875 | `-121.746818 36.808321` | 17144 | 827260 | fixed from exterior face 0 under canonical duplicate-half-edge contract |
| 7386601 | `-121.917238 38.228399` | 0 | 880129 | unchanged exterior witness |
| 7906217 | `-104.840213 39.619783` | 0 | 1839334 | changed by canonical contract from prior nonzero face witness; this means old AuthorPatch output is no longer the correct comparator |
| 9926545 | `-82.631589 28.887243` | 0 | 16153901 | unchanged exterior witness |

The 5693875 repair directly targets the known missing-chain symptom. The 7906217 change is expected under the new RTDL contract and is the reason a fair final comparison must use `Author+RTDLContractPatch`, not the old AuthorPatch output.

## What This Does And Does Not Prove

Proves:

- RTDL now has a deterministic duplicate-half-edge output contract for directed point-location.
- The contract is enforced in the OptiX kernel output, not merely patched in a Python or output-chain layer.
- A controlled duplicate half-edge order-dependence case is fixed.
- A real Block x Water witness point that previously selected exterior now selects the canonical interior face.

Does not prove yet:

- Full Section 5.7 byte-equality.
- Performance.
- That the original author binary follows this contract.
- That `AuthorPatch` without a duplicate-half-edge contract remains the valid comparator.

## Next Required Step

Patch the author baseline into an explicitly named `Author+RTDLContractPatch` variant using the same duplicate-half-edge canonical rule, then compare:

1. original/patched author behavior as historical reference;
2. `Author+RTDLContractPatch`;
3. RTDL Goal4868 output.

If `Author+RTDLContractPatch` and RTDL agree on controlled witnesses and then on a bounded overlay run, the remaining Section 5.7 comparison can proceed under this explicit shared contract. If they disagree, the next debug target is the author-side canonicalization insertion point, not RTDL LSI/PIP again.

## Author+RTDLContractPatch Progress

After the RTDL core proof, the author patched baseline was extended in the remote POD copy:

`/workspace/RayJoin_goal4834_patched_author`

Patch artifact:

`history/internal_docs/goal4868_author_rtdl_contract_patch.diff`

Patch shape:

- `src/map/map.h`
  - adds a per-edge `canonical_edge_ids_` device vector;
  - builds it from unordered scaled endpoint pairs;
  - canonicalizes duplicate half-edges to the smallest edge id;
  - exposes `get_face_id_for_edge_id(eid)` on the device map.

- `src/app/map_overlay_rt.h`
  - changes vertex and midpoint point-location face lookup to call `get_face_id_for_edge_id(eid)`.

Author build:

```bash
cd /workspace/RayJoin_goal4834_patched_author/release
make -j2 polyover_exec
```

Result: build succeeded.

Bounded Block x Water author run:

```bash
release/bin/polyover_exec \
  -poly1 /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb \
  -poly2 /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb \
  -serialize=/dev/shm \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor=0.1 \
  -enlarge=3.5 \
  -check=false \
  -output=/workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt
```

Result:

- exit code: `0`
- elapsed: `285s`
- output size: `3,841,329,807` bytes
- compute timing remained small relative to text output:
  - intersection edges: `25.574 ms`
  - map 0 point-location: `201.274 ms`
  - map 1 point-location: `118.920 ms`
  - compute output polygons: `86.486 ms`
  - write to file: `234345 ms`
- author output summary:
  - map 0 xsects: `649605 518110`
  - map 1 xsects: `649605 529531`
  - total chains: `46224916`
  - total faces: `2581495`

Artifact:

`history/internal_docs/goal4868_author_rtdl_contract_block_water_stderr_with_output.txt`

## RTDL vs Author+RTDLContractPatch Prefix Gate

Full 46M-chain streaming comparison is expensive. The initial full streaming compare was stopped after several minutes because it was CPU-replaying the whole output stream and had not yet produced a summary. To avoid another unbounded "looks busy" run, the comparison was switched to a controlled prefix gate:

1. truncate the author output to the first 100,000 lines;
2. run the RTDL packed streaming comparer against that truncated expected file;
3. accept only the expected first diff at line 100,001 with author `<eof>`.

Command used:

```bash
head -n 100000 \
  /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt \
  > /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head100k.txt

python history/internal_docs/goal4867_block_water_packed_streaming_compare.py \
  --left /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb \
  --right /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb \
  --author-output /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head100k.txt \
  --output-dir /workspace/goal4868_rtdl_vs_author_contract_block_water_prefix100k
```

Result:

- elapsed: `174.175s`
- first diff:
  - line: `100001`
  - author: `<eof>`
  - RTDL: `-87.567445 30.302245`

Interpretation: the first 100,000 lines of RTDL output match `Author+RTDLContractPatch` exactly. The first reported difference is only the expected truncation boundary.

Artifact:

`history/internal_docs/goal4868_rtdl_vs_author_contract_block_water_prefix100k_summary.json`

## Exit Label

`completed_core_duplicate_half_edge_contract__micro_gate_passed__block_water_witness_moved__author_contract_patch_built__prefix100k_match`
