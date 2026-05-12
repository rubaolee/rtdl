# Goal1742 v1.8 Release-Candidate Evidence Packet

## Verdict

`v1_8_release_candidate_packet_ready_for_external_review`

This packet assembles the current v1.8 Python+RTDL release-candidate evidence. It does not authorize a tag, version bump, package upload, or public release. It is ready for independent Claude/Gemini review.

## Intended v1.8 Scope

v1.8 finishes Python+RTDL productization on the source-tree release boundary. v2.0 remains the Python+partner+RTDL milestone.

The accepted partner direction remains:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

For v1.8, that partner direction is a boundary and roadmap rule, not a shipped partner-readiness claim.

## Evidence Chain

### Native Engine App-Agnostic Cleanup

- Goals 1668, 1672, 1676, 1681, 1682, 1688, 1690, 1695, 1697, 1699, 1704, 1708, and 1711 migrated the tracked native release surface away from app-shaped ABI names and recovered source/build integrity.
- Goal1758 migrated the remaining older Apple RT / HIPRT / Oracle / Vulkan `lsi`, `overlay`, and `triangle_probe` native support symbols to generic `segment_pair_intersection`, `shape_pair_relation_flags`, and `triangle_cycle_candidates` terminology, removing that multi-backend source/ABI blocker.
- Goal1708/1711 source recovery and validation closed the post-corruption risk window.
- Goal1714 validated the recovered current source on the pod with RTX 4000 Ada hardware.

### Current Python+RTDL Runtime Evidence

- Goal1716 completed all 16 active Goal1659 current-version pod rows after the GEOS link fix and graph binding fix.
- Goal1718/1720/1722/1723 corrected the cross-version Goal1660 reality, separating real comparable evidence from blocked/excluded/current-only rows.
- Goal1726 added companion evidence for facility, robot, and polygon-set Jaccard boundaries.
- Goals1746/1747 recovered all 14 v1.0 Embree app-level baseline artifacts, including the corrected `ann_candidate_search` `rerank_summary` row.
- Goal1748 classified recovered Embree timing comparability as 4 diagnostic phase mappings, 7 timing-schema mismatches, and 3 missing same-name current artifacts.
- Goal1750 summarized same-contract performance evidence: OptiX has 15 artifact-pair rows with 12 primary same-contract ratios, while Embree has one strict same-contract database row plus the bounded recovered app-level evidence.
- Goal1758 was validated by focused leakage tests, Python runtime `py_compile`, `git diff --check`, and local Linux `make build-embree`; full backend hardware validation for HIPRT, Vulkan, Apple RT, and OptiX remains separate platform evidence.

### Conservative Release Decision Base

- Goal1729 created the v1.6.11 release-candidate evidence packet.
- Goals1730 and 1731 provided independent Claude/Gemini review.
- Goal1732 created the final release decision note.
- Goals1733 and 1734 provided independent Claude/Gemini review of that final decision note.
- Goal1735 recorded final consensus for the conservative Python+RTDL release boundary.
- Goal1736 recorded the commit-ready inventory and protected local file exclusions.

### v1.8-Specific Productization Evidence

- Goal1737 identified v1.8 as close but not release-ready until the release-specific packet, public-doc alignment, packaging/install boundary, version/tag discipline, explicit test matrix, and partner-boundary separation were handled.
- Goal1739 Gemini independently accepted the Goal1737 gap audit.
- Goal1740 aligned the highest-risk public docs and front-door indexes so current main is not described as only the older v1.6 boundary.
- Goal1741 validated the source-tree install boundary and kept packaging metadata explicitly pending rather than silently claiming package-install support.

## Source-Tree Release Boundary

v1.8 is candidate-ready only as a source-tree release boundary unless a separate packaging goal is completed.

Supported invocation pattern:

```text
PYTHONPATH=src:. python <example_or_script>
```

Windows PowerShell equivalent:

```text
$env:PYTHONPATH = "src;."
python <example_or_script>
```

No package-install claim is authorized because the repo still has:

- no `pyproject.toml`
- no `setup.py`
- no `setup.cfg`

## Allowed v1.8 Wording

Allowed:

```text
RTDL v1.8 completes the source-tree Python+RTDL productization boundary for the tracked release surface. Python remains the application/control layer, and RTDL owns the app-agnostic RT-shaped kernel/runtime bridge for supported primitive paths.
```

Allowed:

```text
Current evidence supports source-tree execution with documented `PYTHONPATH` setup and validated CPU-reference smoke paths, plus the reviewed native/pod evidence chain for the bounded release surface.
```

## Blocked Wording

Do not claim:

- v1.8 is package-installable unless a packaging goal adds and validates metadata.
- v1.8 ships Python+partner+RTDL.
- RTDL has universal PyTorch/CuPy support.
- RTDL has general true zero-copy support.
- RTDL accelerates arbitrary PyTorch/CuPy programs.
- RTDL optimizes partner code.
- RTDL accelerates whole applications.
- Selecting `--backend optix` proves a public speedup.
- All backends have identical support or performance.
- The recovered v1.0 Embree app-level rows are public same-contract speedup evidence.

## Required Pre-Release Actions

Before tag/release:

1. Get independent Claude and Gemini review of this updated Goal1742 packet, including the Goal1758 native cleanup.
2. Create a final v1.8 decision/consensus note after those reviews.
3. Re-run the focused v1.8 gate.
4. Inspect `git status --short`.
5. Stage only intended source, docs, tests, reports, reviews, and evidence artifacts.
6. Do not stage protected/local files such as `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`, private SSH keys, old tarballs, or `scratch/`.
7. Bump `VERSION` and tag only if the user explicitly authorizes the release operation.

## Boundary

This packet is ready for external review. It is not a final v1.8 release decision, not a version bump, not a tag authorization, and not a package-install claim.
