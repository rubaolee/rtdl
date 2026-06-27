# Goal1729 v1.6.11 Release-Candidate Evidence Packet

## Verdict

`release_candidate_evidence_ready_with_boundary`

The v1.6.11 Python+RTDL-only release-candidate evidence packet is now coherent enough for final release review. It has real pod hardware build/runtime evidence, all active current-version Goal1659 pod rows, a corrected Goal1660 v1.0/current manifest, 16 real comparable artifact pairs, and companion evidence resolving the three timing-artifact boundaries.

This packet does not publish v1.6.11, move a tag, authorize public speedup wording, or authorize broad RTX/GPU claims.

## Evidence Chain

| Goal | Evidence | Status |
| --- | --- | --- |
| Goal1714 | RTX 4000 Ada pod build, Embree/OptiX source/runtime smoke validation after source recovery | accepted with boundary |
| Goal1716 | 16/16 active current-version Goal1659 pod rows completed and wrote artifacts | accepted with boundary |
| Goal1718 | Raw Goal1660 cross-version attempt showed original v1.0 command-shape mismatch | accepted with boundary |
| Goal1720 | v1.0 OptiX adapter recovered 12 additional v1.0 OptiX artifacts | accepted with boundary |
| Goal1722 | Goal1660 manifest corrected to the observed command reality | accepted with boundary |
| Goal1723 | 16 real comparable artifact pairs consolidated | accepted with boundary |
| Goal1726 | Three Goal1723 timing-artifact boundaries resolved by companion evidence | accepted with boundary |
| Goal1727 | Claude review of Goal1726 | accept-with-boundary |
| Goal1728 | Gemini review of Goal1726 | accept |
| Goal1746-1750 | Post-packet v1.0 Embree app-level recovery and same-contract performance summary | accepted with boundary |

## Counts

- Current-version Goal1659 active pod rows: `16/16`
- Goal1660 matrix rows: `36`
- Goal1660 real comparable rows: `16`
- Goal1660 blocked/excluded/current-only rows: `20`
- Comparable artifact pairs present: `16/16`
- Rows with clean parity or companion evidence: `16/16`
- Unresolved companion-evidence boundaries: `0`

## Corrected Interpretation

The original Goal1660 manifest over-planned tagged-v1.0 Embree rows for legacy scripts that did not expose a true `--backend` selector. Goal1722 corrected this:

- v1.0 OptiX-only rows that can run without `--backend optix` remain comparable rows.
- Unsupported v1.0 Embree rows are recorded as current-only unsupported rows, not failed baselines and not slower/faster timing evidence.
- The comparison set is therefore 16 real artifact pairs, not the original 28-row optimistic plan.

Post-packet clarification: Goal1746 later recovered real v1.0 Embree app-level artifacts for all 14 candidate rows, including the previously long-running `ann_candidate_search` row via `rerank_summary`. Goal1748 classified those recovered rows as 4 diagnostic phase mappings, 7 timing-schema mismatches, and 3 missing same-name current artifacts. Goal1750 therefore preserves the conservative interpretation: OptiX has broad same-contract primary ratios, Embree has one strict same-contract database row plus recovered app-level evidence, and no public speedup wording is authorized.

## Companion Evidence

Goal1726 resolves the three timing-artifact boundaries without rewriting the original timing artifacts:

- `facility_knn_assignment/optix`: validation companions for current and v1.0 both report `matches_oracle=true` and threshold count `80000`.
- `robot_collision_screening/optix`: validation companions for current and v1.0 both report `validated=true`, `matches_oracle=true`, and collision count `3840`.
- `polygon_set_jaccard/optix`: public-safe chunk companions for current and v1.0 both report `status=pass`, `parity_vs_cpu=true`, `chunk_policy.public_safe=true`, and `chunk_copies=1024`.

## Release Boundary

This packet supports final release review for a Python+RTDL-only v1.6.11 release candidate. It does not itself authorize:

- publishing or tagging v1.6.11,
- public speedup wording,
- broad RTX/GPU acceleration claims,
- whole-app speedup claims,
- true zero-copy claims,
- Python+partner+RTDL v2.0 claims.

Final release action requires an explicit user decision and final release consensus. Public performance wording must be separately reviewed and scoped to exact subpaths if used at all.

## Next Action

Run independent review on this packet. If accepted, prepare a final release decision note that either:

1. authorizes a conservative v1.6.11 Python+RTDL-only release/tag with no public speedup claims, or
2. holds release for a clearly named remaining blocker.
