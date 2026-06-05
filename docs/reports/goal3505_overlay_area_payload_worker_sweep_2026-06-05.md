# Goal3505 Overlay Area Payload Worker Sweep

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3505 sweeps the opt-in Goal3504 parallel payload preparation route across
worker counts on the same RTX A5000 pod. This determines a measured worker-count
recommendation instead of assuming that more worker processes always help.

All runs use the same public-CDB overlay route:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --component-bounds-filter --device-tile-task-planner --device-planner-repeats 3 --resident-cupy-inputs --executor-repeats 3 --single-triangulation-payload-evidence --parallel-payload-prepare-evidence
```

## Pod Evidence

Artifacts:

- `docs/reports/goal3505_overlay_area_payload_worker_sweep_w2_pod_2026-06-05.json`
- `docs/reports/goal3505_overlay_area_payload_worker_sweep_w4_pod_2026-06-05.json`
- `docs/reports/goal3505_overlay_area_payload_worker_sweep_w8_pod_2026-06-05.json`
- `docs/reports/goal3505_overlay_area_payload_worker_sweep_w12_pod_2026-06-05.json`
- `docs/reports/goal3505_overlay_area_payload_worker_sweep_w16_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `74a8f65b0239e6b540b524b5387aa2e3ba5fa9a9`

## Results

| Payload workers | Geometry+payload prepare | Device planner best | Executor best | Total abs error |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 3.166s | 0.0471s | 0.0145s | 9.228e-09 |
| 4 | 2.032s | 0.0543s | 0.0149s | 9.228e-09 |
| 8 | 1.441s | 0.0471s | 0.0146s | 9.228e-09 |
| 12 | 1.702s | 0.0542s | 0.0150s | 9.228e-09 |
| 16 | 2.266s | 0.0583s | 0.0152s | 9.228e-09 |

Best measured worker count on this pod: **8 workers**.

Interpretation:

- More workers help until 8 on this dataset and pod.
- 12 and 16 workers regress, likely from process startup, WKB serialization,
  memory pressure, and scheduling overhead overtaking useful parallelism.
- The device planner and executor are stable enough across runs to confirm that
  the sweep is about preparation, not downstream GPU execution.
- Exact-area correctness remains stable across every run.

## Boundary

This sweep recommends 8 workers for this pod/dataset route only. It does not
authorize a global default for every machine or dataset. It does not make
prepared-payload construction device-native, does not claim true zero-copy, does
not claim full overlay completion, and does not authorize release or public
speedup wording.

The next engineering target remains a deeper payload residency/cache or
native/partner prepared-payload route. Goal3505 only chooses the best current
CPU-parallel setting for the benchmark route.
