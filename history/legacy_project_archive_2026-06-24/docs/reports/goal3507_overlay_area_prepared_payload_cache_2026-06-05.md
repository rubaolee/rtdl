# Goal3507 Overlay Area Prepared Payload Cache

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3507 adds an opt-in prepared-payload cache for the v2.8 public-CDB overlay
area benchmark route. This is a reusable workflow optimization: once Shapely
geometry repair and simple-polygon component triangulation have produced RTDL's
generic prepared payload columns, a later run can reload those columns instead
of rebuilding them.

The cache is outside the native engine. It serializes generic prepared simple
polygon component payload columns, source-shape/component mappings, and the
geometry WKB needed by the exact oracle. It does not add app-specific native
logic and it does not change the exact area executor.

## Pod Evidence

Artifacts:

- `docs/reports/goal3507_overlay_area_prepared_payload_cache_write_pod_2026-06-05.json`
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_read_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `19b36ccd59d6ff51b75fdf9268ebce01e43ffc28`

Both artifacts use the same public-CDB route:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --component-bounds-filter --device-tile-task-planner --device-planner-repeats 3 --resident-cupy-inputs --executor-repeats 3 --single-triangulation-payload-evidence
```

The cache-write run also uses:

```text
--payload-workers 8 --parallel-payload-prepare-evidence --payload-cache-dir /tmp/rtdl_goal3507_cache --payload-cache-mode refresh --payload-cache-evidence
```

The cache-read run uses:

```text
--payload-cache-dir /tmp/rtdl_goal3507_cache --payload-cache-mode read --payload-cache-evidence
```

## Results

| Route | Geometry+payload prepare | Cache load | Cache write | Device planner best | Executor best | Total abs error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Goal3505 best rebuild, 8 workers | 1.441s | 0.000s | 0.000s | 0.0471s | 0.0146s | 9.228e-09 |
| Goal3507 cache refresh/write | 1.607s | 0.000s | 1.356s | 0.0559s | 0.0146s | 9.228e-09 |
| Goal3507 cache read | 0.355s | 0.355s | 0.000s | 0.0550s | 0.0150s | 9.228e-09 |

The first cached read reduces the preparation stage from the best measured
8-worker rebuild (`1.441s`) to JSON cache load (`0.355s`), about **4.07x** for
that stage on this pod and dataset. Compared with the pre-parallel Goal3502
single-triangulation route (`5.058s` combined geometry+payload prepare), the
cached read is about **14.27x** faster for this preparation stage.

Correctness and downstream workload shape are unchanged:

- Relation rows: 4,543
- Supported relation rows: 2,149
- Exact positive rows: 1,086
- Observed positive rows: 1,086
- Planned triangle pairs: 4,070,240
- Total absolute area error: `9.227797193034348e-09`
- Max per-relation absolute error: `1.0414238360567651e-09`

## Interpretation

This closes the current "repeat-run payload residency" gap for the public-CDB
overlay route without pretending that the native engine now owns polygon
repair, general overlay, or persistent device memory. The improvement matters
for benchmark iteration because the expensive CPU preparation step can be
reused across repeated timing runs, planner probes, executor probes, and partner
continuation experiments.

The write path is intentionally not counted as a speedup win. It performs the
same parallel rebuild and then serializes the cache, so it costs more than a
plain rebuild. The benefit appears on later read-mode runs.

## Boundary

The cache is host-side JSON/WKB reuse of prepared generic payload columns. It is
not true zero-copy, not device-resident payload persistence, not full polygon
overlay, and not a RayJoin paper reproduction. It does not authorize public
speedup, RT-core speedup, release, or `rtdl beats RayJoin` wording.

The next deeper target, if we continue this lane, is a binary or device-resident
prepared-payload cache with a measured lifetime/ownership contract. Goal3507 is
the conservative file-cache step before that harder runtime feature.
