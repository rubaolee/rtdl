# Goal4298: v2.11 Embree CPU + Current Partner Reference Packet

Date: 2026-06-11

Status: implemented and validated on local Linux.

## Purpose

Goal4298 starts the v2.11 lane by making the Embree CPU fallback path visible for the
current benchmark-app generation. The goal is not to tune performance yet. The goal is
to define and validate a clean executable packet for:

- the ten current benchmark apps;
- Embree CPU routes where the current app exposes an Embree front door;
- the current CPU partner reference where no Embree front door existed at the
  time of Goal4298;
- all-thread CPU execution environment setup for local Linux runs.

In short: this is the v2.11 Embree CPU plus current CPU partner reference packet.

This packet replaces the older Goal2037-era Embree CPU planning shape for current
work. Goal2037 was useful, but it targeted older app rows and should not be used as
current v2.11 benchmark evidence.

## Scope

The new registry is:

`src/rtdsl/current_embree_cpu_partner_reference.py`

The new runner is:

`scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py`

The new test is:

`tests/goal4298_v2_11_embree_cpu_partner_reference_packet_test.py`

## Current Rows

| App | Row | Route |
| --- | --- | --- |
| `hausdorff_xhd` | `hausdorff_xhd_embree_cpu_directed_summary` | Embree CPU primitive |
| `spatial_rayjoin` | `spatial_rayjoin_pip_count_embree_cpu_generic_kernel` | Embree CPU plus Python continuation |
| `rt_dbscan` | `rt_dbscan_embree_cpu_prepared_rows` | Embree CPU plus Python continuation |
| `robot_collision` | `robot_collision_embree_cpu_prepared_buffers` | Embree CPU primitive |
| `contact_manifold` | `contact_manifold_embree_cpu_native_collect_k` | Embree CPU primitive |
| `raydb_style` | `raydb_style_embree_cpu_count_primitive_first` | Embree CPU primitive-first grouped count |
| `barnes_hut` | `barnes_hut_embree_cpu_node_coverage_prepared` | Embree CPU plus Python continuation |
| `librts_spatial_index` | `librts_spatial_index_embree_cpu_aabb_index` | Embree CPU primitive |
| `rtnn` | `rtnn_embree_cpu_ann_candidate_quality_reference` | Embree CPU candidate-quality front door added by Goal4308 follow-up |
| `triangle_counting` | `triangle_counting_embree_cpu_native_summary` | Embree CPU primitive |

RTNN was intentionally different in the original Goal4298 packet: it used a
Numba CPU partner reference because the benchmark app did not yet expose an
Embree front door. Goal4308 follow-up removes that exception by adding
`ann_embree_quality`, a bounded Embree CPU front door for the RTNN benchmark
app's 2-D ANN candidate-quality contract. This does not claim the 3-D RTNN
ranked-summary route is implemented on Embree, and it does not make a paper
reproduction claim.

## Runner Behavior

The runner emits progress for every row:

```text
[v2.11-embree-cpu] 1/10 start ...
[v2.11-embree-cpu] 1/10 done ... status=...
```

It also sets a consistent all-thread CPU environment before executing rows:

- `OMP_NUM_THREADS`
- `TBB_NUM_THREADS`
- `MKL_NUM_THREADS`
- `OPENBLAS_NUM_THREADS`
- `NUMEXPR_NUM_THREADS`
- `RTDL_EMBREE_THREADS`

The runner supports `--dry-run`, `--only`, `--threads`, `--timeout-scale`, and
`--output-json` so local Linux runs can be resumed and inspected without silent hangs.

## Claim Boundary

This packet does not authorize release action, package-install wording, public speedup
wording, whole-app acceleration wording, broad RT-core wording, NVIDIA/AMD/Intel GPU
performance wording, paper-reproduction wording, true-zero-copy wording, automatic
partner selection, or app-specific native-engine logic.

In particular, Embree here means CPU RT fallback evidence. It is not evidence for
NVIDIA RT-core performance and it is not Intel GPU performance wording.

## Local Linux Validation

Local Linux validation target:

redacted local Linux host

Initial SSH probe from Windows timed out on 2026-06-11, then the host came back.
The final validation artifact is:

`docs/reports/goal4298_v2_11_embree_cpu_partner_reference_local_linux.json`

Result:

- Host: redacted local Linux host
- Python: `/usr/bin/python3`
- CPU threads: `8`
- Embree library: `build/librtdl_embree.so`
- Runner result: `all_pass: true`
- Row result: `10 / 10 pass`
- Claim-boundary violations: none reported by the runner

The slowest row is expectedly CPU-bound:

- `librts_spatial_index_embree_cpu_aabb_index`: wrapper elapsed about `132s`,
  app-reported median query time about `43.9s`.

The historical RTNN row passed after Goal4299:

- `rtnn_numba_cpu_partner_quality_reference`: wrapper elapsed about `1.3s`;
- Numba score rows generated on partner device: `true`;
- top-k ranking status: `reference_host_rank_after_device_score_rows`;
- host rank materialization: `true`, explicitly marked as v2.11 reference debt.

Goal4308 follow-up supersedes that current registry row with:

- `rtnn_embree_cpu_ann_candidate_quality_reference`;
- mode: `ann_embree_quality`;
- scope: Embree CPU candidate-subset top-1 quality reference for the 2-D ANN
  candidate contract;
- boundary: not 3-D RTNN ranked-summary, not full RTNN paper reproduction, not a
  speedup claim.

## Acceptance Criteria

- Registry covers all ten current benchmark apps exactly once.
- Goal4298 historical artifact: nine rows exercised Embree CPU and RTNN used a
  Numba CPU partner reference.
- Current Goal4308 registry: all ten rows exercise Embree CPU, with RTNN using
  `ann_embree_quality` for the 2-D ANN candidate-quality contract.
- Registered commands do not route through OptiX or CuPy and do not require RT cores.
- Runner sets all-thread CPU environment variables and prints per-row progress.
- Runner fails closed on any claim-boundary flag set to `true` in app output.
- Local unit tests pass.
- Local Linux execution result is added before using this as v2.11 Embree evidence.
