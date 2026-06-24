# Goal4171: RT-DBSCAN Road3D 2M One-Shot Probe

Status: accepted bounded one-shot evidence; no route promotion.

## Purpose

Goal4169 showed that the road-like 2M all-predicate wrapper remains faster than
the current grouped-stream route for warmed measured runs. Goal4171 measures the
same road-like 2M shape with `repeat=1` and `warmup=0` to expose the one-shot
cost a user pays when no warm measured replay exists.

## Pod Evidence

Artifact:

`docs/reports/goal4171_rtdbscan_road3d_2m_oneshot_probe_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `72a4aedc6425646e00cf903c395c6b007cbd3dcc`
- Dataset: `road3d`
- Point count: 2,097,152
- Partition cell factor: `0.25`
- Repeat/warmup: repeat 1, warmup 0

## Result

| Route | One-shot measured run (s) | Same RT-DBSCAN signature | Notes |
| --- | ---: | --- | --- |
| current grouped-stream Numba | 34.941951 | reference | conservative current route |
| prepared direct-status component signature | 20.119836 | generic component schema only | 1.737x faster, but not the RT-DBSCAN app signature shape |
| predicate all-true direct-status wrapper | 25.772315 | yes | 1.356x faster, fast path observed |

The all-predicate wrapper remains above parity in a true one-shot run. It also
keeps the exact RT-DBSCAN signature shape and records
`all_predicate_fast_path: true` plus `border_candidate_updates: 0`.

## Interpretation

The one-shot all-predicate wrapper is slower than the warmed Goal4169 wrapper
(`25.77s` versus `20.51s`) but still faster than the current grouped-stream
route. The direct-status signature phase itself reports about `20.13s`, while
the full one-shot wrapper reports `25.77s`. That gap is the remaining practical
target: first-run/count-threshold/wrapper overhead, not border work.

This does not solve mixed-predicate rows. For mixed predicate flags, Goals4165
through 4168 still require explicit policy-aware semantics and no hidden border
policy selection.

## Boundary

This report does not authorize automatic route selection, automatic partner
selection, automatic factor selection, release, public speedup wording, broad
RT-core wording, whole-app benchmark claims, paper-reproduction claims,
app-specific engine logic, native ABI additions, AMD performance claims, or
true-zero-copy claims.
