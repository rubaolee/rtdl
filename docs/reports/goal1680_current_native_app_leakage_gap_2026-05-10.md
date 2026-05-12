# Goal1680 Current Native App-Leakage Gap

Date: 2026-05-10

Status: current local gap snapshot after the Goal1673, Goal1674, Goal1681,
Goal1682, Goal1688, Goal1690, Goal1695, Goal1697, and Goal1699 native
cleanup work.

## Verdict

The native app-agnostic release gate still fails. It remains pending
independent review and pod/hardware execution evidence, even though the tracked lowercase
app-shaped native callable/export families are now zero.

The current strict scan over `src/native` reports:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 9 |
| Strict regex occurrences | 14 |
| Known uppercase `RTDL_DB_*` constant false-positive symbols | 9 |
| Known uppercase `RTDL_DB_*` constant false-positive occurrences | 14 |
| Remaining app-shaped callable/export symbols | 0 |

The false-positive constants must remain documented in the superseding audit;
they must not be silently ignored.

## Remaining Real Symbol Families

No real app-shaped native callable/export families remain in the strict
tracked-family scan. The only remaining strict hits are uppercase
`RTDL_DB_*` data-kind/operator constants, which are documented false positives
rather than lowercase C ABI endpoints.

The cleanup deltas remain intact:

- no `pose`-named OptiX native symbols remain in the strict real-symbol set;
- `rtdl_oracle_polygon` remains absent;
- no `pip`-named native symbols remain in the strict real-symbol set;
- no `hausdorff`-named native symbols remain in the strict real-symbol set;
- no `bfs_expand`-shaped Embree/HIPRT/OptiX/Oracle/Vulkan symbols remain in
  the strict real-symbol set;
- no Apple RT `bfs_discover` native symbols remain in the strict real-symbol
  set;
- no `knn`-named native ABI symbols remain in the strict real-symbol set;
- no `polygon`-named native ABI symbols remain in the strict real-symbol set;
- no `db`-named lowercase native ABI symbols remain in the strict real-symbol
  set;
- the replacement OptiX group symbols remain present;
- the replacement point/primitive any-hit packet symbols remain present;
- the replacement max-distance nearest-candidate symbol remains present;
- the replacement frontier/edge traversal packet symbols remain present;
- the replacement Apple RT frontier discover native symbols remain present.
- the replacement k-closest-hit native symbols remain present.
- the replacement shape and shape-pair native symbols remain present.
- the replacement columnar payload, multi-predicate scan, predicate match, and
  grouped-reduction native symbols remain present.

## v1.8 Meaning

This report is the current work queue for the app-agnostic native-engine part
of the v1.8 Python+RTDL track. It supersedes the Goal1668 dirty baseline only
for current counts after the first local migrations; it does not relax the
release gate.

The next app-agnostic cleanup should target one remaining family at a time:

1. `pip` / point-in-polygon native exports into generic point/primitive
   any-hit or candidate-packet terminology. (Completed by Goal1681.)
2. `polygon` segment/pair/set exports into generic geometry candidate and
   reduction descriptors.
   (Completed by Goal1697.)
3. `knn` rows into generic bounded candidate collection.
   (Completed by Goal1695.)
4. `db` dataset helpers into generic columnar predicate/reduction descriptors.
   (Completed by Goal1699.)
5. `bfs` graph helpers into generic frontier/edge packet traversal.
   (Completed by Goal1688 and Goal1690.)
6. `hausdorff` reduction into Python-owned app semantics over generic nearest
   candidates. (Completed by Goal1682.)

Blocked wording remains:

```text
RTDL native internals are fully app-agnostic.
```
it or candidate-packet terminology. (Completed by Goal1681.)

## v1.8 Release-Gate Status

The native app-agnostic release gate still fails on pod / hardware execution
evidence even though the strict source scan is clean. The release wording

```text
RTDL native internals are fully app-agnostic.
```

remains explicitly blocked until distinct-AI consensus is recorded and a
hardware-validated pod run is produced.
