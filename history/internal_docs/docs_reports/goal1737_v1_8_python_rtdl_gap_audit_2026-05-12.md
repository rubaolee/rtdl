# Goal1737 v1.8 Python+RTDL Gap Audit

## Verdict

`v1_8_close_but_not_release_ready`

The v1.6.11 release-candidate evidence chain gives v1.8 a strong technical base: the tracked native release surface has been migrated to app-agnostic ABI language, recovered source has been validated, current-version pod evidence exists, and the final v1.6.11 consensus permits a conservative Python+RTDL release boundary.

v1.8 is not ready to tag yet. The remaining work is mostly productization and release-governance work, not another broad native ABI rewrite.

## Evidence In Hand

- Goal1668 through Goal1708 migrated and audited the app-shaped native families into generic engine terminology.
- Goal1711 through Goal1716 produced Linux/pod build and current-version runtime evidence after source recovery.
- Goal1718 through Goal1726 produced the cross-version Goal1660 evidence, manifest corrections, comparable artifact consolidation, and companion evidence for the previously ambiguous validation boundaries.
- Goal1729 through Goal1736 produced the v1.6.11 release-candidate packet, independent Claude/Gemini reviews, final release decision note, final consensus, and commit-ready inventory.
- Goal1735 consensus permits only conservative Python+RTDL wording and keeps broad speedup, arbitrary RTX, partner, and whole-application acceleration claims blocked.

## Remaining v1.8 Blockers

### 1. Release-Specific v1.8 Decision Artifact

v1.8 still needs its own final decision packet. The v1.6.11 chain can be cited as evidence, but v1.8 needs an explicit release artifact that says exactly what is shipping, what is excluded, and what wording is allowed.

Required output:

- `docs/reports/goal17xx_v1_8_release_candidate_evidence_packet_2026-05-12.md`
- a paired test that checks the allowed and blocked v1.8 claims
- independent Claude and Gemini reviews using distinct AI systems
- a final v1.8 decision/consensus note after review

### 2. Public Documentation Alignment

Several public-facing docs still describe the project from an older v1.6 lens. That wording was correct historically, but it can confuse a v1.8 reader unless it is framed as historical context.

Docs that need a careful v1.8 pass include:

- `docs/current_architecture.md`
- `docs/current_main_support_matrix.md`
- `docs/performance_model.md`
- `docs/README.md`
- root `README.md`
- `docs/public_documentation_map.md`

Allowed v1.8 wording should say the tracked release native surface is app-agnostic under the current gate. It must not claim universal partner zero-copy, arbitrary PyTorch/CuPy acceleration, or broad speedups.

### 3. Packaging And Install Boundary

The repo currently has no Python packaging metadata:

- no `pyproject.toml`
- no `setup.py`
- no `setup.cfg`

That means v1.8 must choose one of two paths:

- declare the release source-tree based and document the exact supported invocation path, or
- add packaging metadata, install tests, wheel/sdist expectations, and platform caveats.

Until that decision is made and tested, Python+RTDL productization is incomplete.

### 4. Version And Tag Discipline

`VERSION` still reads `v1.5`. That is correct until an explicit release operation is authorized.

For v1.8, do not bump `VERSION`, tag, or publish from this audit alone. The release sequence should happen only after the v1.8 decision packet, documentation alignment, packaging/install decision, and independent reviews are complete.

### 5. Test Scope Definition

The focused final evidence gate is healthy, but v1.8 needs an explicit release test matrix that distinguishes:

- required local tests
- required Linux/pod tests
- allowed skips
- historical tests that are superseded by app-agnostic ABI migrations
- tests requiring unavailable SDKs or hardware

This prevents v1.8 from silently inheriting a too-small or too-broad test promise.

### 6. Partner Track Remains v2.0

The accepted roadmap still holds:

- `v1.8` finishes Python+RTDL productization.
- `v2.0` finishes Python+partner+RTDL.

The partner design remains protocol first, PyTorch reference first, CuPy conformance alongside it, and engine absolutely app-agnostic throughout. v1.8 should not absorb unfinished partner promises.

## Practical Distance To v1.8

Engineering state: roughly `80-90%` of the hard technical evidence is already in place, because the native app-agnostic migration, source recovery, pod smoke, current-version Goal1659 evidence, cross-version Goal1660 evidence, and independent v1.6.11 reviews are done.

Release state: not ready. The remaining blockers are the v1.8-specific release packet, public doc alignment, packaging/install decision, explicit test matrix, and independent final review.

## Recommended Next Slice

Start with a v1.8 release-candidate packet that cites Goals 1668 through 1736, then update public docs to reflect the current app-agnostic tracked surface without overclaiming partner readiness or performance.

After that, decide whether v1.8 is source-tree-only or package-installable. If package-installable, packaging metadata and install tests become mandatory before release.

## Boundary

This audit is not a release command, not a version bump, and not a tag authorization. It is a gap map for the remaining v1.8 Python+RTDL productization work.
