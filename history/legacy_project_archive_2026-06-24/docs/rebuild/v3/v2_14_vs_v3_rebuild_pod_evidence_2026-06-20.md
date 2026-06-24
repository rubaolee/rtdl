# V2.14 Versus V3 Rebuild Pod Evidence

Status: Phoenix V3 benchmark evidence report, 2026-06-20.

Verdict: V3 is technically recoverable and now has clean current-side benchmark
coverage, but it is still not a published user-ready major release.

This report answers the release-owner question: does current V3, treated as the
first version users should trust, deliver both usability and high performance
with benchmark-app proof?

The honest answer is:

```text
The core benchmark evidence is much better: the current V3 tree passes the
standard comparison suite, the strengthened suite, and the scale-profile suite
on the pod. V3 should continue. V3 still must not be published until public
docs/tutorials are rebuilt from exact reviewed rows and every performance claim
is row-scoped.
```

## Evidence Sources

Pod:

- Host: `root@213.173.108.14 -p 11592`.
- GPU: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`, 20475 MiB.
- V2.x baseline: tag `v2.14`, commit
  `8384a38376567fe518d89721453eb4433de08312`.
- Current V3 state: uploaded source-tree snapshot from the V3 rebuild branch.
- Native libraries built for both trees: Embree and OptiX.

Initial V2.14 comparison artifact:

```text
remote: /root/rtdl_v3_rebuild_20260620/artifacts/v2_14_vs_v3_rebuild_non_numba_serious_20260620_051207
local:  docs/rebuild/v3/evidence/v2_14_vs_v3_rebuild_non_numba_serious_20260620_051207
```

Current-side Phoenix artifacts:

```text
remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_current_goal2626_clean_env_20260620_055523
local:  docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_current_goal3828_full_clean_20260620_060412
local:  docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_current_goal2636_full_clean_20260620_060726
local:  docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_gpu_python_env_gate_20260620_061058
local:  docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058

remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_gpu_python_env_gate_script_20260620_062113
local:  docs/rebuild/v3/evidence/v3_gpu_python_env_gate_script_20260620_062113
```

All-app calibrated OptiX-vs-Embree artifact:

```text
remote: /root/rtdl_v3_rebuild_20260620/artifacts/v3_claim_grade_all_benchmarks_calibrated_20260620
local:  docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620
report: docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
```

This run covers all ten promoted benchmark apps with 40 ok rows, 0 failed rows,
and 19 comparable Embree-vs-OptiX ratios. It is the preferred all-app
performance evidence for rebuilding V3 docs.

## What Changed In The Phoenix Evidence Run

The initial serious run showed real value but also P0 failures:

- `spatial_rayjoin_optix_prepared_full_route` failed with an OptiX invalid-value
  error.
- `raydb_optix_partner_resident_count` and
  `raydb_optix_partner_resident_sum` failed because `torch` was absent.
- Numba-required scale rows failed before RTDL semantics due a CUDA/Numba PTX
  toolchain mismatch.

The Phoenix evidence run fixed the current-side blockers:

- Spatial RayJoin prepared all-workload route now completes.
- RayDB partner-resident rows now complete with PyTorch installed and gated.
- Numba scale rows now complete with an explicit CUDA 12.4 nvcc/libnvvm prefix.
- CuPy RawKernel, Torch CUDA tensor, and Numba CUDA JIT smoke checks all pass in
  the same pod environment.

## Current Clean Run Summary

| Suite | Current V3 Phoenix result | Meaning |
| --- | ---: | --- |
| `goal2626_standard_all_rows` | 22 ok / 0 failed | Standard Embree/OptiX comparisons now run cleanly. |
| `goal2636_standard_all_rows` | 28 ok / 0 failed | Strengthened authored workloads now run cleanly. |
| `goal3828_full_clean` | 10 pass / 0 fail | All ten scale-profile benchmark apps execute, including Numba rows. |
| GPU Python environment gate | pass | CuPy RawKernel, Torch CUDA, and Numba CUDA JIT all pass, including the reusable script-backed gate. |

Important boundary: the `goal3828` scale-profile rows explicitly do not
authorize release or public speedup wording. They are coverage and route-health
evidence, not a release certificate.

## V3 Versus V2.14

The initial comparison remains important. It showed:

- Current V3 passes triangle-counting OptiX device-column rows where v2.14 fails
  with PTX/toolchain runtime errors.
- Shared successful V2.14 and current V3 rows are usually similar in raw OptiX
  timing.
- The strongest V3-over-V2.14 statement today is runability and route health,
  not a broad "V3 is faster than V2.x" claim.

So the permitted high-level statement is:

```text
Current V3 repairs and stabilizes a Python-hosted RTDL benchmark surface and
keeps strong OptiX-over-Embree rows. It also fixes current-side runability for
routes that were blocked in the initial V3 rebuild run and preserves the
triangle-counting improvement over v2.14.
```

The non-permitted statement is:

```text
V3 broadly outperforms V2.x across all benchmark apps.
```

## Current OptiX Over Embree Signals

These are current-side pod ratios from the Phoenix evidence run. Values above 1.0 mean
OptiX was faster than Embree for the measured row.

### Goal2626 Standard Rows

| App | Row group | OptiX speedup vs Embree |
| --- | --- | ---: |
| `rt_dbscan` | `dbscan_cluster_signature` | superseded by same-contract packet |
| `raydb_style` | `raydb_grouped_count` | 277.838x |
| `raydb_style` | `raydb_grouped_sum` | 263.753x |
| `triangle_counting` | `triangle_count_rt_graph_2a1_summary` | 56.029x |
| `robot_collision` | `prepared_collision_flags` | 5.099x |
| `barnes_hut` | `node_coverage_prepared_threshold_decision` | 2.760x |
| `hausdorff_xhd` | `hausdorff_threshold_decision` | 2.525x |
| `contact_manifold` | `generic_aabb_broadphase_collect_k` | 1.290x |
| `rtnn` | `prepared_3d_ranked_summary` | 1.098x |
| `spatial_rayjoin` | `rayjoin_all_backend_query_summary` | 0.034x |
| `librts_spatial_index` | `aabb_index_all_count_only` | 0.065x |

The two rows below 1.0 are not OptiX speedup claims. They are important because
they tell users where the measured route should not be marketed as an RT-core
win.

The RTDBSCAN row in this broad table is also not current public speedup
evidence. It was later superseded by the optimized same-contract component
signature packet, which qualifies exactly
`component_union_clustered3d_65536_524288_repeat5_row_scoped` and nothing
broader.

They also require an explanation, not just a warning. The detailed explanation
is [V3 Negative Route Explanations](v3_negative_route_explanations_2026-06-20.md).
In short:

- `spatial_rayjoin/rayjoin_all_backend_query_summary` is a tiny fixture
  route-health row: LSI has `row_count=1`, overlay has `row_count=0`, PIP has
  `row_count=6`, and the protocol is `warmup=0`, `repeat=1`. It is not a
  RayJoin paper-scale speed row.
- `librts_spatial_index/aabb_index_all_count_only` is a small synthetic
  generic AABB-index row with `paper_reproduction=false` and
  `paper_equivalent_dataset=false`. It is not a LibRTS authors-code or
  paper-equivalent timing.
- A later calibrated generic AABB row at 32768 boxes and 32768 queries replaces
  the small row for current performance interpretation, with an 814.339x
  OptiX-over-Embree signal. That positive row is still only a generic RTDL AABB
  route, not LibRTS authors-code or paper-equivalent timing.
- Both rows must stay in the "negative/mixed" section and must not be compared
  to paper results.

### Goal2636 Strengthened Rows

| App | Row group | OptiX speedup vs Embree |
| --- | --- | ---: |
| `spatial_rayjoin` | `rayjoin_overlay_seed_authored_tiled_x512` | 5419.291x |
| `spatial_rayjoin` | `rayjoin_lsi_authored_tiled_x512` | 365.448x |
| `triangle_counting` | `triangle_count_rt_graph_2a1_cliques_20000` | 114.229x |
| `triangle_counting` | `triangle_count_rt_graph_2a1_cliques_5000` | 36.632x |
| `spatial_rayjoin` | `rayjoin_pip_authored_tiled_x512` | 22.748x |
| `rtnn` | `rtnn_clustered_65536_ranked_summary` | 4.365x |
| `barnes_hut` | `barnes_hut_node_coverage_bodies_8192` | 2.735x |
| `hausdorff_xhd` | `hausdorff_threshold_copies_4096` | 2.596x |
| `hausdorff_xhd` | `hausdorff_threshold_copies_16384` | 2.025x |
| `barnes_hut` | `barnes_hut_node_coverage_bodies_32768` | 1.858x |
| `hausdorff_xhd` | `hausdorff_threshold_copies_65536` | 1.633x |
| `rtnn` | `rtnn_shell_65536_ranked_summary` | 1.162x |
| `rtnn` | `rtnn_uniform_65536_ranked_summary` | 0.959x |

The RTNN uniform row is mixed and should not be described as a universal RTNN
speedup.

## GPU Python Environment Gate

The current pass requires an explicit GPU Python environment:

| Component | Evidence |
| --- | --- |
| CuPy | `cupy-cuda12x==14.1.1`; RawKernel smoke passes; local/runtime CUDA reports `12090`. |
| PyTorch | `torch==2.6.0+cu124`; `torch.cuda.is_available()` true; CUDA tensor smoke passes. |
| Numba | `numba==0.65.1`; CUDA JIT smoke passes with `NUMBA_CUDA_PREFIX` set to `nvidia-cuda-nvcc-cu12==12.4.131`. |
| CUDA runtime packages | `nvidia-cuda-nvrtc-cu12==12.9.86`, `nvidia-cuda-runtime-cu12==12.9.79`, `nvidia-cuda-nvcc-cu12==12.4.131`. |

There is still a warning from `cuda-bindings` being built for CUDA major 13
while the driver supports CUDA 12. The smoke and benchmark rows pass, but this
warning should remain visible in setup guidance until the dependency set is
made quieter.

## Benchmark-App Classification

| App | Current classification | User-facing meaning |
| --- | --- | --- |
| `hausdorff_xhd` | row-scoped M7, not release | One exact threshold_summary row is qualified; no full Hausdorff or X-HD claim. |
| `spatial_rayjoin` | internal evidence, not M7 | Authored routes are useful evidence, but RayJoin author RT remains faster on PIP and no Spatial RayJoin row is qualified. |
| `rt_dbscan` | row-scoped M7, not release | One exact component_union row is qualified; the old huge all-app ratio remains forbidden. |
| `robot_collision` | row-scoped M7, not release | One exact no-probe collision_flag_stream row is qualified; no full robot-planning claim. |
| `raydb_style` | dependency-gated row-scoped M7, not release | One exact grouped_reduction sum row is qualified; whole-app RayDB and count rows remain blocked. |
| `barnes_hut` | internal evidence, not M7 | Current evidence is fused/partner-route evidence; no Barnes-Hut RT-core speedup row is qualified. |
| `librts_spatial_index` | row-scoped generic AABB M7, not paper reproduction | One exact generic AABB candidate-stream row is qualified; not LibRTS authors-code timing. |
| `rtnn` | boundary lesson, not M7 | Hot-path wins exist, but wall timing regresses on all current distributions. |
| `triangle_counting` | row-scoped M7, not release | One exact synthetic prepared_graph_chunk row is qualified; no RT-Graph paper or graph-database claim. |
| `contact_manifold` | boundary lesson, not M7 | Query/collect-k are scoped positives, but wall timing is slower and the full contact solver remains app-owned. |

Machine-readable classification lives at:

```text
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
```

## What V3 Solves Now

V3 can now be described as solving this V2.x problem:

```text
V2.x had promising RTDL capability but did not give users a stable, evidence-led
answer to which benchmark routes worked, which backend to choose, and which
partner dependencies were required. V3 rebuilds that into a Python-hosted RTDL
surface with row-scoped benchmark evidence and explicit backend/partner gates.
```

This is still not enough to publish:

```text
V3 is not yet a polished user release. The benchmark evidence is repaired; the
user-facing docs, tutorials, setup gates, and release language still need to be
rebuilt from the repaired evidence.
```

## Required Work Before V3 Can Be Published

P0:

1. Rebuild public docs and tutorials from these repaired artifacts only.
2. Add setup instructions that reproduce the GPU Python environment gate.
3. Split performance claims by row using the all-app calibrated artifact:
   OptiX wins, partner-gated routes, qualified hot routes, and non-claims.
4. Keep V2.14 comparison wording honest: V3 improves runability and route
   health, not broad V2.x speed across every shared row.
5. Explain the two negative rows before publication:
   `spatial_rayjoin/rayjoin_all_backend_query_summary` and
   `librts_spatial_index/aabb_index_all_count_only`.
6. Add a final release gate that fails if public docs claim release readiness
   without the repaired artifact set.

P1:

1. Make the CUDA package set quieter and easier to install.
2. Rerun the repaired suite on a second machine or the local Linux GPU box.
3. Ask Claude or another reviewer to audit the repaired V3 evidence and docs
   before any release declaration.

## Final Repair-Pass Decision

V3 should continue and should not be deleted. It now has enough serious pod
evidence to justify rebuilding the user surface.

V3 should also not be published yet. The release gate is:

```text
Publish only after the docs/tutorials/setup path are rebuilt from these passing
artifacts and a reviewer confirms that no public claim exceeds the row-level
evidence.
```

## Goal-Level Decision Audit

Decision: keep V3 alive, but keep release authorization false.

1. Did I make a foolish decision?

   No. The foolish decision would be either deleting V3 after fixable benchmark
   failures, or calling V3 released just because the repaired rows now pass.

2. What actions would make the decision foolish?

   Hiding the environment gate, ignoring mixed routes, or converting internal
   benchmark success into broad public speedup language.

3. Was there another path?

   Yes. V3 could have been abandoned, or the failing rows could have been
   quietly removed. Both would lose useful technical value.

4. What different path is now being used?

   Keep V3, repair the benchmark surface, record exact artifacts, classify every
   app, and allow public docs only after they match the repaired evidence.
