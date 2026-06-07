# Goal3740 - Benchmark-App Adequacy After Goal3737

Date: 2026-06-07

Status: internal performance triage; not a release packet and not public
speedup authorization.

## Purpose

Goal3737 gave RayJoin a real improvement: the safe mixed public-CDB composite
now reaches `324.324x` geomean versus the all-CuPy same-contract baseline across
1024/2048/4096 chains, with all counts matching. The next project step is to
stop treating the benchmark suite as a pile of isolated rows and decide, app by
app, what is already good enough and what still needs major generic
runtime/primitive work.

Goal3740 records that decision in a machine-checkable matrix. The matrix was
then refreshed after Goals3742/3744/3746 closed the RT-DBSCAN and Barnes-Hut
Numba-reference gaps:

- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `tests/goal3740_benchmark_app_adequacy_after_goal3737_test.py`

## Reader-Facing Adequacy Table

| Benchmark app | Current reading | Adequacy | Numba reference needed? | Next generic work |
| --- | --- | --- | --- | --- |
| `hausdorff_xhd` | Positive v2.9 row (`1.019555x`) plus separate RTDL/OptiX X-HD evidence; not an X-HD paper win claim. | adequate | no; Numba exact reference already exists | Use as AMD nearest-witness parity target. |
| `spatial_rayjoin` | Strong contract-specific result after Goal3737: safe-mixed geomean `324.324x`, min `183.302x`, 4096 `624.255x` versus all-CuPy. | strong | yes | Make broad-CDB closed-shape/PIP exact without CuPy-only policy, or reduce generic overlay active-scan/containment work. |
| `rt_dbscan` | Near parity in the v2.9 packet (`0.997206x`); Goal3742/3744 add Numba grid component labeling and OptiX-to-Numba bridge evidence. | adequate | no | Treat as covered for Numba-reference purposes; next major work is HIPRT fixed-radius parity. |
| `robot_collision` | Near parity (`0.987619x`) on prepared any-hit flags. | near_parity | no | Treat as no-regression unless larger pose batches expose material overhead. |
| `contact_manifold` | Positive row (`1.219528x`). | adequate | no | Keep as primitive-only bounded witness reference. |
| `raydb_style` | Count is `1.009085x`; sum is `1.585627x` after generic grouped-i64 fast path. | adequate | no | Preserve primitive-first path; use for AMD grouped-reduction parity. |
| `barnes_hut` | Resident evidence exists, and Goal3746 adds a Numba CUDA JIT exact-force reference at `0.754x`-`0.893x` of CuPy RawKernel on A5000. | adequate | no | Treat as covered for Numba-reference purposes; deeper hierarchical vector primitives are future work. |
| `librts_spatial_index` | Clean resident same-contract evidence is slightly positive (`1.005864x`), composite row near parity. | adequate | no | Keep as prepared-index no-regression and AMD AABB-query parity target. |
| `rtnn` | Positive row (`1.061225x`) with prepared ranked-summary evidence. | adequate | no | Use as prepared fixed-radius aggregate parity target for AMD. |
| `triangle_counting` | Positive row (`1.029580x`) and fastest route is primitive-only. | adequate | no | Keep as primitive-only graph-summary target. |

## Current Interpretation

The benchmark suite is no longer dominated by weak rows, but it is also not
done:

- `spatial_rayjoin` is now strong in the conservative mixed same-contract
  comparison, but still exposes the next deep runtime problem: generic
  closed-shape/topology exactness and generic scalar-count correction without
  materializing unnecessary rows.
- `rt_dbscan` and `barnes_hut` now have measured Numba references. They are not
  promoted as universal wins over CuPy, but users no longer need CuPy RawKernel
  as the only high-performance reference for those continuation shapes.
- `robot_collision` is slightly negative but close enough to treat as
  no-regression unless a larger batch exposes a material issue.
- `raydb_style`, `contact_manifold`, `rtnn`, `triangle_counting`,
  `librts_spatial_index`, and `hausdorff_xhd` are adequate for the current
  internal performance lane.

## Numba Reference Scope

The next Numba work should be narrow and app-owned:

| Priority | App | Reason |
| --- | --- | --- |
| P1 | `spatial_rayjoin` | Closed-shape/topology policy should have a Numba reference for app-owned continuation; native engine remains generic. |

Numba reference paths do not mean hidden partner selection. Users still choose
partners explicitly. The project provides measured reference implementations
for supported partners.

## AMD HIPRT Preparation Scope

The AMD lane should start only after a primitive map, not by porting benchmark
apps directly. Initial HIPRT targets:

1. segment-pair exact count,
2. shape-pair active-count executor,
3. nearest-witness output columns plus grouped max,
4. fixed-radius grouped/ranked summary,
5. grouped i64 count/sum,
6. prepared AABB query,
7. bounded witness collection.

The first AMD goal is functional parity. Performance comes after parity.

## Claim Boundary

Goal3740 does not authorize:

- release or tag action,
- public speedup claims,
- whole-app acceleration claims,
- broad RT-core claims,
- RayJoin paper reproduction claims,
- RTDL-beats-RayJoin claims,
- true-zero-copy claims,
- hidden automatic partner selection,
- app-specific native-engine logic.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3740_benchmark_app_adequacy_after_goal3737_test
```
