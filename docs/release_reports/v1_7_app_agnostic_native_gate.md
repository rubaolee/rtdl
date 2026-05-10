# v1.7 App-Agnostic Native-Engine Gate

This is a release gate for the next architectural track after the current
Python+RTDL release surface.

## Gate Rule

RTDL must not publish the claim:

```text
RTDL native internals are fully app-agnostic.
```

until a superseding audit proves that the release-surface native engine has no
app-shaped, domain-shaped, or workload-shaped native exports.

## Required Audit

The gate audit must scan `src/native/` native export and callable surfaces for
at least these leakage terms:

- `db`
- `pip`
- `bfs`
- `robot`
- `pose`
- `polygon`
- `knn`
- `hausdorff`
- `jaccard`

The next expanded audit must also search for broader semantic leakage terms
that can encode app knowledge without using the initial directive vocabulary:

- `table`
- `column`
- `edge`
- `vertex`
- `agent`
- `trajectory`

Expanded-term false positives must be documented explicitly in the superseding
gate report; they must not be silently ignored.

The current baseline is documented in:

- [Goal1668 Native-Engine App-Agnostic Directive Response](../reports/goal1668_native_engine_app_agnostic_directive_response_2026-05-10.md)
- [Goal1603 Stable Native-Path App-Leakage Audit](../reports/goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md)

## Passing Condition

The gate passes only if one of these is true:

- the strict leakage audit returns zero app/domain/workload symbols for the
  release-surface native engine, or
- any remaining historical symbols are mechanically quarantined outside the
  release surface and cannot be called by public runners.

Quarantine is only an interim migration mechanism. A quarantined native
app-shaped surface must either be deleted or moved behind a non-release legacy
build path before RTDL can publish the v2.0-level claim that native internals
are fully app-agnostic.

## Failing Condition

The gate fails if public runners still depend on native symbols with app-shaped
names or semantics, including database, graph, robot/pose, polygon/GIS,
Hausdorff, Jaccard, or KNN-specific native backdoors.

Wrapper-backed Python APIs do not satisfy this gate if the underlying native
symbol remains app-shaped.

## Performance Rescue Direction

Performance regressions caused by removing native app backdoors must be solved
through:

- generic RTDL primitive packets,
- generic reductions,
- partner tensor handoff,
- true zero-copy or reduced-copy mechanisms,
- prepared generic input/output buffers.

Do not solve regressions by reintroducing app-specific C++/CUDA entry points.
