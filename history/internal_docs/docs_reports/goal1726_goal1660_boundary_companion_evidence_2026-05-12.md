# Goal1726 Goal1660 Boundary Companion Evidence

## Verdict

`accept-with-boundary`

The three Goal1723 boundary rows now have pod-generated companion evidence. This resolves the evidence hygiene issue in the comparable artifact consolidation, but it still does not authorize v1.6.11 release, tagging, or public speedup wording.

## Companion Artifacts

| Row | Current artifact | v1.0 artifact | Result |
| --- | --- | --- | --- |
| `facility_knn_assignment/optix` | `docs/reports/goal1726_v1_6_11_facility_validation_companion_optix.json` | `docs/reports/goal1726_v1_0_facility_validation_companion_optix.json` | Both report `matches_oracle=true` and threshold count `80000`. |
| `robot_collision_screening/optix` | `docs/reports/goal1726_v1_6_11_robot_collision_validation_companion_optix.json` | `docs/reports/goal1726_v1_0_robot_collision_validation_companion_optix.json` | Both report `validated=true`, `matches_oracle=true`, and collision count `3840`. |
| `polygon_set_jaccard/optix` | `docs/reports/goal1726_v1_6_11_polygon_set_jaccard_public_safe_chunk_optix.json` | `docs/reports/goal1726_v1_0_polygon_set_jaccard_public_safe_chunk_optix.json` | Both report `status=pass`, `parity_vs_cpu=true`, and `chunk_policy.public_safe=true` with `chunk_copies=1024`. |

## Consolidation Impact

Goal1723 now records:

- Planned comparable rows: `16`
- Artifact pairs present: `16`
- Rows with clean parity or companion evidence: `16`
- Timing-artifact boundary rows: `3`
- Companion resolutions: `3`
- Unresolved boundaries: `0`

The original timing artifacts are intentionally not rewritten. Instead, the consolidation records the original timing-row boundary and the companion artifact that resolves it.

## Boundary

This is still artifact hygiene, not release authorization. The companion evidence supports a cleaner final review packet, but speedup calculations, public wording, release tagging, and v1.6.11 publication remain blocked pending final review.
