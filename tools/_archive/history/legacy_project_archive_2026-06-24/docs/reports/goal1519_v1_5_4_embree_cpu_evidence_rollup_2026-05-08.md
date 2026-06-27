# Goal 1519: Embree CPU Evidence Rollup

## Verdict

The current v1.5.4 Embree CPU lane has enough tracked evidence to support
continued Python+RTDL semantic hardening and app-envelope measurement, but it
does not support public speedup wording, broad polygon/GIS claims, broad RTX
claims, whole-app acceleration claims, true zero-copy claims, stable
`COLLECT_K_BOUNDED` promotion, or release action.

The strongest measured CPU-side pattern is not "Embree is always faster." The
stronger and more useful result is narrower: compact summaries and prepared
native structures can reduce repeated Python/app work and output
materialization in selected app envelopes, while some native-assisted polygon
paths remain slower when exact refinement and JSON output dominate.

## Evidence Matrix

| Goal | Scope | Host | Acceptance signal | Performance shape | Claim boundary |
| --- | --- | --- | --- | --- | --- |
| Goal1514 | Embree CPU promotion lane | Windows + Linux planning/test guidance | Focused semantic lane defined for bounded collection, reductions, ABI, app groups, and native smoke slices | No new timing claim | CPU-only guidance; not NVIDIA or release evidence |
| Goal1515 | Native Embree Linux validation | Linux `192.168.1.20` checkout | Native Embree app slice passed `Ran 17 tests OK` | Runnability/parity evidence, not timing evidence | Does not authorize speedup or broad app claims |
| Goal1516 | Materialization summary performance | Linux `lx1`, Embree `(4, 3, 0)` | All parity passed; tracked JSON/Markdown artifacts | Event hotspot summary improved `1.274x`, `1.338x`, `1.139x`; service coverage was mixed at `1.030x`, `1.108x`, `0.903x` | Selected CPU Embree app modes only |
| Goal1517 | Prepared summary reuse performance | Linux `lx1`, Embree `(4, 3, 0)` | Tracked JSON/Markdown artifacts and artifact guard tests | Prepared run-only outlier/DBSCAN summary phases improved about `1.485x` to `1.627x` versus one-shot, excluding prepare cost | Repeated app summary phases only |
| Goal1518 | Polygon native-assisted performance | Linux `192.168.1.20` checkout | Tracked JSON/Markdown artifacts and Windows/Linux guard tests | Polygon-pair summary becomes helpful at larger output volume (`1.794x` at 4096 copies), but Jaccard Embree is slower than CPU in the measured envelope (`0.642x`, `0.228x`, `0.068x`) | Exact measured polygon modes only; no broad polygon/GIS claim |

## What This Proves

- Embree is useful as the CPU semantic promotion lane for app-name-free
  primitive contracts, reduction parity, candidate collection behavior, ABI
  routing, and cross-platform smoke validation.
- Compact summaries can avoid row materialization and reduce JSON payload size
  when the app only needs aggregate results.
- Prepared native state can matter for repeated workloads when the setup cost is
  amortized and the measured scope is explicitly run-only after preparation.
- Polygon workloads must be reported by exact app envelope because native
  candidate discovery alone is not enough to guarantee end-to-end improvement.

## What This Does Not Prove

- It does not prove NVIDIA RT-core performance.
- It does not prove OptiX parity or OptiX speed.
- It does not prove whole-app acceleration.
- It does not prove broad database, GIS, graph, polygon, or Jaccard speedups.
- It does not prove true zero-copy between Python and native engines.
- It does not promote `COLLECT_K_BOUNDED` out of experimental status.

## Recommended Next Work

| Track | Next action | Why |
| --- | --- | --- |
| Embree CPU | Add more strict parity and overflow guards around bounded collection and compact reductions | This prepares primitives before expensive pod work |
| Embree CPU | Keep measuring exact app envelopes where materialization, preparation, and JSON output are separable | This tells us whether RTDL work or Python/output work dominates |
| OptiX pod | Replay only the same-contract slices that already have Embree semantics | This avoids wasting pod time on unclear contracts |
| Docs/review | Ask external reviewers to check claim boundaries before any release-facing wording | This prevents accidental broad performance claims |

## Artifact Pointers

- `docs/reports/goal1514_v1_5_4_embree_cpu_promotion_lane_2026-05-08.md`
- `docs/reports/goal1515_v1_5_4_embree_native_linux_validation_2026-05-08.md`
- `docs/reports/goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08.md`
- `docs/reports/goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08.json`
- `docs/reports/goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08.md`
- `docs/reports/goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08.json`
- `docs/reports/goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08.md`
- `docs/reports/goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08.json`

## Claim Boundary

Goal1519 is a rollup of already tracked CPU Embree evidence. It adds no new
performance measurement and does not authorize public speedup wording, broad
RTX wording, broad polygon/GIS wording, whole-app claims, true zero-copy
wording, stable `COLLECT_K_BOUNDED` promotion, or release action.
