# Goal2626 Full Standard Matrix After Gap Closures

Date: 2026-05-27

This internal report records the first full standard Embree-vs-OptiX matrix
after the RayDB, Spatial RayJoin, Triangle Counting, and Barnes-Hut path fixes.
It is not public speedup wording.

## Evidence

Pod command supplied by the user:

```text
ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519
```

Working key used from this Mac:

```text
/Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Run details:

```text
commit ac0abfb3b47d29d10dab10701838fe530513271f
scale standard
GPU NVIDIA RTX A5000, driver 565.57.01, 24564 MiB
CUDA 12.6
OptiX SDK /root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64
```

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --artifact-dir /root/rtdl_goal2626_full_standard_after2633 \
  --timeout-sec 1200
```

Artifact copies:

- `docs/reports/goal2626_full_standard_after2633_pod/summary.json`
- `docs/reports/goal2626_full_standard_after2633_pod/summary.md`

## Result Table

| App / group | Embree sec | OptiX sec | OptiX speedup vs Embree | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Barnes-Hut node coverage | `0.0350694` | `0.00837431` | `4.19x` | Same-contract prepared threshold decision fixed the old mismatch. |
| Contact manifold native collector | `0.0112383` | `0.0122115` | `0.92x` | Collector-only row; app-owned witness discovery still dominates outside the primary metric. |
| Hausdorff threshold decision | `0.099465` | `0.030408` | `3.27x` | Clean prepared threshold RT win. |
| LibRTS AABB index | `20.7959` | `1.0113` | `20.6x` | Clean high-volume AABB query RT win. |
| RayDB grouped count | `0.1858` | `0.000731998` | `254x` | Partner-resident grouped count path replaces the data-movement fallback. |
| RayDB grouped sum | `0.236247` | `0.00403211` | `58.6x` | Partner-resident grouped sum path; still not an RT-core claim. |
| Robot collision flags | `0.00932187` | `0.00260676` | `3.58x` | Prepared collision flag path remains OptiX-positive. |
| RT-DBSCAN cluster signature | `20.5097` | `1.27554` | `16.1x` | Grouped-stream OptiX path remains strongly positive. |
| RTNN ranked summary | `0.256645` | `0.011392` | `22.5x` | Prepared 3-D ranked summary path remains strongly positive. |
| Spatial RayJoin full benchmark route | `0.0205852` | `0.000567341` | `36.3x` | OptiX now uses prepared PIP, LSI, and overlay-seed route. |
| Triangle counting RT-2A1 summary | `0.0383412` | `0.000597202` | `64.2x` | Generic prepared ray/triangle RT path replaces the old fallback. |

## Main Conclusion

The earlier negative rows were mostly path-selection or contract problems, not
evidence that RTDL/OptiX is intrinsically slower. After fixing the promoted
benchmark rows, OptiX is faster than Embree on every promoted comparison except
the contact-manifold native collector row.

The contact-manifold exception is expected: the measured row is a bounded i64
collector over already discovered witness rows. It does not yet use generic RT
witness discovery, so it should not be interpreted as an RT traversal
performance result.

## Remaining Work

- Make contact-manifold use generic RT witness discovery before treating it as
  an RT-throughput benchmark.
- Add larger/scale-aware Spatial RayJoin fixtures because the default fixture
  is still tiny even though the route is now correct.
- Continue separating RT-core claims from partner-resident non-RT wins,
  especially RayDB.
