# RTDL v0.9.8 Support Matrix

Status: released as `v0.9.8`.

This matrix describes the released `v0.9.8` boundary. For the broader
engine feature matrix, use `docs/features/engine_support_matrix.md`. This file
only describes the v0.9.8 RTX app public-claim surface.

## Public RTX Wording Surface

| App / sub-path | Public wording status | Public claim allowed for v0.9.8 | Boundary |
| --- | --- | --- | --- |
| `road_hazard_screening / prepared_native_compact_summary_40k` | reviewed | yes | prepared native compact-summary traversal/count sub-path at 40k copies only |
| `database_analytics` | blocked | no | saved evidence is below public speedup threshold |
| `polygon_set_jaccard` | blocked | no | correctness-ready path lacks same-scale reviewed speedup evidence |

## Current Public Matrix Facts

- Reviewed public RTX wording rows: `11`.
- Newly reviewed row in this release window:
  `road_hazard_screening / prepared_native_compact_summary_40k`.
- `database_analytics` public speedup wording: `blocked`.
- `polygon_set_jaccard` public speedup wording: `blocked`.

## Backend Notes

- OptiX/RTX evidence for this release is bounded to saved Goal1206/Goal1208
  artifacts and reviewed public wording.
- A successful `--backend optix` run is not by itself a public NVIDIA RT-core
  speedup claim.
- The road-hazard public claim excludes default app behavior, GIS/routing, row
  output, Python orchestration, and whole-app performance.
- This release package does not add new HIPRT AMD GPU validation or Vulkan
  parity claims.

## Release-Gate Evidence

- Goal1206 merged pod/recovery intake: road hazard positive same-scale public
  candidate; DB below public threshold; Jaccard speedup blocked.
- Goal1208 public wording decision: road hazard reviewed, DB/Jaccard blocked.
- Goal1214 full local discovery: `2366` tests OK, `196` skips.
- Goal1215 release-surface docs: `64` tests OK.
- Goal1216 release-candidate audit: valid, no immediate pod needed.
- Goal1217 version marker sync repaired the pre-release baseline marker to `v0.9.6`.
- Goal1221 release action bumped the current marker to `v0.9.8`.
- Goal1218 authorization gate: release evidence valid, release not authorized
  until v0.9.8 package/final authorization review.

## Not Allowed

- broad app-suite speedup;
- all-app RT-core acceleration wording;
- broad DB speedup;
- polygon/Jaccard speedup;
- whole-app road-hazard speedup;
- release scope beyond the audited `v0.9.8` boundary.
