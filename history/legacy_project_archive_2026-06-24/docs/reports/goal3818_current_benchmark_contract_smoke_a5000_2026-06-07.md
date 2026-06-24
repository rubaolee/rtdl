# Goal3818 Current Benchmark Contract Smoke On A5000

Date: 2026-06-07

## Purpose

Run one bounded current command for each of the ten promoted benchmark apps on
the A5000 pod after the v2.10 documentation and alias cleanup. This is a
contract-smoke packet: it proves the benchmark front doors are executable on a
healthy NVIDIA/OptiX host and records any command-contract corrections. It is
not a long-run performance matrix.

## Environment

- Pod: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000
- Commit under test: `b56a8927`
- Repository path: `/root/rtdl_goal3788_clean_1780857956`
- `RTDL_OPTIX_LIBRARY`: `build/librtdl_optix.so`
- `RTDL_EMBREE_LIBRARY`: `build/librtdl_embree.so`
- Python path: `.pydeps_goal3788_numba:src:.`

The pod initially had Embree and HIPRT built, but no visible OptiX library. The
OptiX SDK was present at `/root/vendor/optix-sdk`, so `make build-optix
OPTIX_PREFIX=/root/vendor/optix-sdk` was run before the smoke packet.

## Result Summary

The first pass executed ten rows. Eight passed immediately. Two rows failed for
expected, fail-closed command-contract reasons and then passed with corrected
current commands.

| App row | First command status | Repaired status | Lesson |
| --- | --- | --- | --- |
| `hausdorff_xhd` | failed | passed | `--require-rt-core` requires `--backend optix --optix-summary-mode directed_threshold_prepared`; the doc now shows the exact fail-closed command shape. |
| `spatial_rayjoin_pip_count` | passed | not needed | Current prepared OptiX PIP count route runs. |
| `rt_dbscan_numba` | passed | not needed | Current OptiX threshold flags plus Numba prepared-grid continuation runs. |
| `robot_collision` | passed | not needed | Current OptiX prepared device-count route runs. |
| `contact_manifold` | failed | passed | `COLLECT_K_BOUNDED` intentionally fails closed when capacity is too small; the doc now shows a current OptiX native collect command with enough witness capacity. |
| `raydb_style` | passed | not needed | Current primitive-first OptiX grouped-count route runs. |
| `barnes_hut_numba` | passed | not needed | Current no-RawKernel Numba exact-force reference route runs. |
| `librts_spatial_index` | passed | not needed | Current OptiX prepared AABB-index route runs. |
| `rtnn_plan` | passed | not needed | Current ranked-summary typed-stream/Numba plan route runs. |
| `triangle_counting` | passed | not needed | Current OptiX summary triangle-count route runs. |

Artifacts are saved under:

`docs/reports/goal3818_current_benchmark_contract_smoke_a5000/`

Important files:

- `summary.json` records the first ten-command pass.
- `repair_summary.json` records the two repaired commands.
- `*.stdout.txt` and `*.stderr.txt` retain bounded output for each row.

## Documentation Corrections

The smoke packet exposed two learner-facing issues and one stale label class:

- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md` now describes a
  current RTDL user, not a `v2.8` user, and shows the correct
  `directed_threshold_prepared` command for `--require-rt-core`.
- `examples/v2_0/research_benchmarks/contact_manifold/README.md` now includes a
  current OptiX `native_collect_k` command with `--witness-capacity 32` for the
  small grid smoke case.
- `docs/tutorials/v2_app_building.md`,
  `docs/tutorials/segment_polygon_workloads.md`, and
  `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` no longer teach
  current users as `v2.8` users.

## Boundary

This packet does not authorize release action, package-install wording, public
speedup wording, broad RT-core wording, whole-app acceleration wording,
true-zero-copy wording, automatic partner selection, paper reproduction claims,
AMD hardware/performance claims, or app-specific native-engine logic.

The A5000 evidence is NVIDIA/OptiX control evidence. It does not replace the
separate AMD/HIPRT functional validation lane.
