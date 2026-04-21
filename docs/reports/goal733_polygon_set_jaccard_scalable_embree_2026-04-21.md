# Goal 733: Polygon-Set Jaccard Scalable Embree Characterization

Date: 2026-04-21

## Scope

Goal 733 adds `--copies` support to
`examples/rtdl_polygon_set_jaccard.py` so the public Jaccard app can be tested
at larger scales while keeping the default behavior unchanged.

The default remains:

- `--copies 1`
- one authored fixture
- one Jaccard result row

The Embree app path now reuses the positive-only candidate helper introduced
for Goal732:

- Embree `segment_intersection` for polygon-edge crossing candidates
- Embree positive-hit `point_in_polygon` for containment candidates
- CPU/Python exact grid-cell set-area refinement

This avoids the old full `overlay_compose` left x right matrix materialization
inside the app.

## Correctness

Focused tests verify:

- area totals scale with `copies`
- the Jaccard ratio is preserved under tiling
- Embree native-assisted output matches CPU Python reference at scale
- invalid copy counts are rejected

Command:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal733_polygon_set_jaccard_scalable_embree_test
```

Results:

- macOS: 3 focused tests passed
- Linux: 3 focused tests passed

## Performance Evidence

Measurement:

- `run_case(...)` plus `json.dumps(...)`
- CPU Python reference versus Embree native-assisted path
- copies 64, 256, 1024
- 3 repeats

macOS:

| Copies | CPU reference median | Embree median | Embree / CPU speedup |
| ---: | ---: | ---: | ---: |
| 64 | 0.0032s | 0.0106s | 0.31x |
| 256 | 0.0127s | 0.0333s | 0.38x |
| 1024 | 0.0542s | 0.1360s | 0.40x |

Linux:

| Copies | CPU reference median | Embree median | Embree / CPU speedup |
| ---: | ---: | ---: | ---: |
| 64 | 0.0063s | 0.0182s | 0.34x |
| 256 | 0.0254s | 0.0718s | 0.35x |
| 1024 | 0.1030s | 0.2819s | 0.37x |

Raw evidence:

- `docs/reports/goal733_polygon_set_jaccard_scalable_perf_local_2026-04-21.json`
- `docs/reports/goal733_polygon_set_jaccard_scalable_perf_linux_2026-04-21.json`

## Boundary

This goal improves the Embree app implementation by avoiding full overlay
matrix materialization and gives us scalable evidence. It does not make Embree
faster than the CPU reference for this tiled Jaccard fixture.

The reason is structural: polygon-set Jaccard emits one compact result row
already, and exact set-area refinement is still CPU/Python-owned. Embree is
correct and better bounded than the old all-pairs overlay-matrix path, but this
is not a performance win over the CPU reference today.
