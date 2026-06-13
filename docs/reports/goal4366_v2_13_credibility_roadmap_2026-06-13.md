# RTDL v2.13 Credibility Roadmap

Status: accepted plan; not a release packet and not new public speedup wording.

## Current Baseline

| Evidence | Measurement | Meaning | v2.13 action |
| --- | ---: | --- | --- |
| v2.12 release table | 11 scoped rows, 10 promoted apps | baseline is complete but row-scoped | freeze as the v2.13 starting point |
| RayJoin LSI same stream | OptiX 0.336 ms, Embree 14.539 ms, Embree/OptiX 43.28x, RayJoin RT/RTDL 2.44x | strong RT-core value row and RTDL OptiX faster than RayJoin RT for scalar count | use Goal4367 as the authors-code comparison baseline |
| RayJoin PIP same stream | OptiX 6.04 ms, Embree 19.428 ms, Embree/OptiX 3.22x, RayJoin RT faster 7.28x | clear OptiX-over-Embree improvement, but current RTDL optimization debt versus RayJoin RT | Goal4368 improves the exact route; keep optimizing exact refinement |
| Contact Manifold | Embree/OptiX 0.55x, faster backend `embree` | reasonable tiny-row Embree win; needs human-scale batching | include in human-scale timing packet |
| RTNN | Embree/OptiX 1.18x, faster backend `optix` | near-parity backend row; not an RT-core neighbor-search claim | keep backend-only unless a true RT-core row is built |

## Row Reasonability Review

| Row | Embree / OptiX | Faster | Verdict | Explanation | v2.13 action |
| --- | ---: | --- | --- | --- | --- |
| barnes_hut | 1.938x | `optix` | `reasonable_scoped_rt_core_value` | Moderate OptiX win is credible because this row is a native node-coverage threshold decision, not Barnes-Hut force integration. | Keep the force-vector and paper-reproduction boundary visible. |
| contact_manifold | 0.548x | `embree` | `reasonable_embree_faster_tiny_row` | Embree winning is credible for this tiny bounded collect-k witness row; launch and orchestration overhead can dominate the RT path. | Add a human-scale repeated batch before any public wording. |
| hausdorff_xhd | 2.571x | `optix` | `reasonable_scoped_rt_core_value` | The OptiX win is plausible for a prepared threshold count where traversal dominates more than output materialization. | Keep exact-distance and whole-app claims blocked. |
| LibRTS prepared AABB query | 18.798x | `optix` | `reasonable_scoped_rt_core_value` | Large OptiX win is credible after the native Embree AABB route replaced the old columnar fallback; this is a prepared query median. | Scale box/query counts and report prepare amortization separately. |
| raydb_style | 22.147x | `optix` | `reasonable_scoped_rt_core_value` | Large OptiX win is credible for a prepared ray/triangle grouped count; the row is not SQL, DBMS, or typed stream timing. | Keep DB wording blocked and add typed hit-stream evidence separately. |
| robot_collision | 1.595x | `optix` | `reasonable_small_total_win` | Small tail-total OptiX win is credible because the compact-flag contract is already tiny; traversal wins are partly hidden by fixed overhead. | Report native traversal and tail-total side by side. |
| rt_dbscan | 54.955x | `optix` | `reasonable_scoped_rt_core_value` | Large OptiX win is credible because both rows hold the same Numba continuation fixed and differ mainly in the RTDL geometric prefilter. | Preserve the partner-fixed route and avoid whole-app DBSCAN wording. |
| rtnn | 1.183x | `optix` | `reasonable_not_rt_core_claim` | Near parity is credible and is not an RT-core neighbor-search claim because the current OptiX row is a prepared ranked-summary route. | Either build a true RT-core neighbor-search row or keep this as backend-only. |
| Spatial RayJoin LSI same-stream scalar count | 43.275x | `optix` | `reasonable_strong_rayjoin_rt_core_row` | Strong OptiX win is credible: same RayJoin-exported stream, scalar count, exact count match, and no RTDL row materialization. | Retain in the Goal4367 authors-code packet with stream hashes. |
| Spatial RayJoin PIP same-stream scalar count | 1.177x | `optix` | `reasonable_but_v2_13_optimization_debt` | Near parity against Embree and slower-than-RayJoin RT are credible because exact membership refinement and generic front-door overhead dominate the current row. | Use Goal4368 as the improved exact baseline, then keep attacking exact refinement. |
| triangle_counting | 72.685x | `optix` | `reasonable_scoped_rt_core_value` | Large OptiX win is credible for a prepared ray/triangle any-hit count; this is query/count timing rather than whole application time. | Keep prepared-query wording and add larger human-scale repeats. |

## PIP Phase Debt

The current PIP OptiX row is explainable but not satisfying: hot query median 6.04 ms, candidate write median 1.861 ms, candidate download median 0.023 ms, and exact refinement median 4.092 ms.

## V2.13 Goals

| Priority | Goal | Deliverable | Acceptance gate |
| ---: | --- | --- | --- |
| 0 | `freeze_v2_12_release_boundary`: Freeze v2.12 as the bounded release baseline | A stable v2.12 source-tree tag and comparison packet used only as baseline evidence. | Do not move the v2.12 tag without explicit maintainer decision. All v2.13 wording must distinguish baseline evidence from new claims. |
| 1 | `rayjoin_authors_code_comparison_packet`: Compare against RayJoin authors code on the same streams | A table covering RayJoin grid, LBVH, and RT logs versus RTDL OptiX and RTDL Embree for LSI and PIP scalar-count contracts. | Same exported query stream schema and hashes are reported. RayJoin Query ms, build/index ms, and RTDL hot query ms are separate columns. Each speedup column states which direction is good. LSI and PIP each have a reasonability paragraph tied to measured phases. |
| 2 | `pip_exact_membership_optimization`: Turn Spatial RayJoin PIP from explanation debt into optimization evidence | A measured PIP packet that either closes the gap to RayJoin RT or proves why the exact RTDL contract remains dominated by refinement. | Candidate generation, download, exact refinement, and Python/front-door timing are visible. The row is rejected for public speedup wording unless the observed speedup has a phase-level explanation. A successful optimization keeps the exact prepared-points count contract and count agreement. |
| 3 | `embree_cpu_fairness_hardening`: Harden the Embree CPU side as the serious multicore baseline | A repeatable Embree CPU protocol with thread counts, warmups, repeats, native traversal time, and fallback detection for every promoted row. | Every compared Embree row uses a native route or explicitly names the partner continuation. Thread/environment settings are included in each run packet. Fallback and boundary-limited rows are excluded from release-facing speedups. |
| 4 | `human_scale_timing_packet`: Make tiny rows human-scale without changing the contract | A timing packet that reports 1-10 second aggregate batches plus per-query medians for sub-ms rows. | Batching is repeat-only and does not smuggle in unrelated setup work. Per-query and aggregate timing are both reported. Contact Manifold, Robot Collision, LibRTS, and triangle-counting tiny rows are included first. |
| 5 | `public_wording_packet`: Produce the public comparison wording only after row-level explanations pass | A publication table where every speedup has a same-contract basis, a direction definition, and an observed-speedup explanation. | No broad RT-core speedup wording. No whole-application speedup wording unless end-to-end evidence exists. No RTDL-beats-RayJoin wording except for exact rows where the authors-code comparison supports it. Every surprising row has a written explanation or is marked not publishable. |
| 6 | `amd_gpu_defer_gate`: Defer AMD GPU work until the NVIDIA-vs-Embree story is credible | A go/no-go decision for AMD after v2.13 credibility gates pass. | RayJoin authors-code comparison packet is complete. PIP either improves or has a phase-level explanation accepted for public wording. The public wording packet passes with zero unexplained speedup rows. |

## AMD GPU Decision

Prepare AMD GPU now: `False`.

Prepare AMD GPU only after v2.13 has an accepted RayJoin authors-code comparison, a PIP optimization/explanation packet, and a public wording packet with zero unexplained rows.

The current scientific question is NVIDIA RT cores versus Embree CPU cores. Adding AMD now would widen the matrix before the NVIDIA-vs-CPU story is publication-clean.

## Completion Contract

v2.13 is done only when the RayJoin authors-code comparison, PIP optimization or phase-level explanation, Embree fairness hardening, human-scale timing packet, and public wording packet all pass. A row with an unexplained speedup is a failed row, not an excuse.

Validation status: `accept`.
