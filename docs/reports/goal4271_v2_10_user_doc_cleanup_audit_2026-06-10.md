# Goal4271: v2.10 User Documentation Cleanup Audit

Date: 2026-06-10

Status: complete local documentation cleanup and guard test.

## Purpose

Clean the current user-facing documentation surface so normal learners see one
coherent v2.10 source-tree product story:

- current docs describe v2.10, not older v2.x lanes;
- current partner guidance is primitive-first, user-chosen, and limited to the
  currently recommended CuPy/Numba lane;
- historical evidence remains reachable through history, audit, release-report,
  report, and review paths, but does not interrupt the normal learning path;
- local Markdown links in the current docs resolve.

This cleanup intentionally does not rewrite historical reports, reviews,
handoffs, release archives, audit runbooks, or the future-version to-do list.

## Scope

Audited current-doc paths:

- `README.md`
- top-level current docs under `docs/*.md`
- `docs/learn/**`
- `docs/tutorials/**`
- `docs/features/**`
- `docs/rtdl/**`
- current research doors under `docs/research/**` excluding `archive/` and
  `future_version_to_do_list.md`
- `examples/v2_0/**/README.md`

Excluded as intentionally historical or planning material:

- `docs/reports/**`
- `docs/reviews/**`
- `docs/handoff/**`
- `docs/release_reports/**`
- `docs/history/**`
- `docs/audit/**`
- `docs/directives/**`
- `docs/engineering/**`
- `docs/research/archive/**`
- `docs/research/future_version_to_do_list.md`

## Validation Summary

| Check | Result |
| --- | --- |
| Current-doc stale wording scan | No remaining `PyTorch`, `torch-cuda`, `Triton`, `v2.6`, `v2.7`, `v2.8`, `v2.9`, `stale backend`, or `old Python` hits in the audited current-doc surface. |
| Current-doc local Markdown links and anchors | Passing through `tests.goal4271_v2_10_user_doc_cleanup_test`. |
| Key entrypoints mention v2.10 | Passing through `tests.goal4271_v2_10_user_doc_cleanup_test`. |
| Primitive catalog drift | Regenerated from `src/rtdsl/primitive_catalog.py`; generated catalog now avoids version-stale v2.7 discovery wording. |

Validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4271_v2_10_user_doc_cleanup_test
```

Result:

```text
Ran 3 tests in 2.204s
OK
```

## Files Changed

| File | Problem found | Operation performed |
| --- | --- | --- |
| `README.md` | Current front page still mentioned arbitrary PyTorch/CuPy/Numba acceleration, Triton pause guidance, and historical v2.8/v2.6/v2.3 links in the normal path. | Narrowed partner wording to current CuPy/Numba guidance, removed Triton from the active rule, removed the historical matrix link from the current v2.10 section, and simplified history links. |
| `docs/README.md` | Current docs index still surfaced the historical v2.8 benchmark matrix as a current reference row. | Removed the historical matrix row and cleaned history-directory wording. |
| `docs/app_engine_support_matrix.md` | Support matrix status lagged the v2.10 wording from the current release surface. | Updated status and partner wording to the v2.10 source-tree surface. |
| `docs/app_example_quickstart.md` | Advanced partner tutorial row still described a Torch/CuPy path. | Reworded to the current CuPy-oriented OptiX partner-column path. |
| `docs/application_catalog.md` | Output guidance still named PyTorch as a current partner-owned array target. | Reworded output guidance to CuPy or measured Numba continuations. |
| `docs/backend_maturity.md` | Backend maturity summary still carried older partner-role wording. | Updated the current partner rows to NumPy, CuPy, and Numba roles. |
| `docs/capability_boundaries.md` | Capability boundaries still used older arbitrary partner acceleration phrasing. | Updated the current boundary language to CuPy/Numba and v2.10. |
| `docs/current_architecture.md` | Architecture page still had older-release wording and older partner list residue. | Reworded archived-history pointer and current partner boundary. |
| `docs/current_main_support_matrix.md` | Matrix still said v2.6, named Triton as paused current guidance, and treated PyTorch as current partner-side code. | Updated to v2.10, removed Triton from user guidance, and narrowed partner-side code examples. |
| `docs/features/README.md` | Feature index used "old" phrasing in a current-doc rule. | Reworded to archive/archived context. |
| `docs/features/db_workloads/README.md` | Feature home status needed v2.10 alignment. | Updated status wording. |
| `docs/features/engine_support_matrix.md` | Engine support contract used stale-backend wording. | Reworded to local backend library mismatch without implying stale public docs. |
| `docs/features/fixed_radius_neighbors/README.md` | Feature home status needed v2.10 alignment. | Updated status wording. |
| `docs/features/knn_rows/README.md` | Feature home status needed v2.10 alignment. | Updated status wording. |
| `docs/learn/primitive_discovery_workflow.md` | Discovery workflow still named automatic Triton selection in the current negative boundary. | Reworded to generic automatic partner selection. |
| `docs/partner_acceleration_boundaries.md` | Current boundary page still centered PyTorch and v2.6-era guidance, with older Goal305x report pointers. | Rewrote current partner boundary around NumPy/CuPy/Numba, v2.10, and current Goal4266/4267/4270 pointers. |
| `docs/performance_model.md` | Performance model still listed NumPy/PyTorch/CuPy as the current partner set. | Reworded to NumPy/CuPy/Numba. |
| `docs/public_documentation_map.md` | Public map status needed v2.10 alignment. | Updated current learner-surface wording. |
| `docs/quick_tutorial.md` | Quick tutorial described older scenario-specific helpers in the current path. | Reworded those helpers as archived compatibility material. |
| `docs/release_facing_examples.md` | Command archive ended with "older/old" language in a current page. | Reworded to archived command lists and release-specific notes. |
| `docs/research/README.md` | Research door still said current v2.6. | Updated to current v2.10 surface. |
| `docs/research/design_insights_by_benchmark_apps_2026-05-19.md` | Design-insights doc still said CuPy/PyTorch-style partners. | Reworded to CuPy/Numba-style partners. |
| `docs/rtdl/dsl_reference.md` | DSL reference still mentioned PyTorch in current partner contracts and stale backend wording. | Updated current partner and local-library wording. |
| `docs/rtdl/ir_and_lowering.md` | IR/lowering current chain wording lagged v2.10. | Updated current release-chain wording. |
| `docs/rtdl/itre_app_model.md` | ITRE model still used older chronology wording and older partner boundary phrasing. | Reworded archived chronology pointer and current partner boundary. |
| `docs/rtdl/programming_guide.md` | Programming guide called the Python reference path "old." | Reworded as the portable Python reference path. |
| `docs/rtdl_feature_guide.md` | Feature guide still listed NumPy/PyTorch/CuPy and v2.6 Numba lane. | Reworded to NumPy/CuPy plus selected Numba continuations under current v2.10 guidance. |
| `docs/rtdl_primitive_catalog.md` | Generated catalog still referred to v2.7 discovery/planner wording. | Regenerated after updating the renderer and planner/discovery source strings. |
| `docs/runtime_overhead_architecture.md` | Runtime-overhead note still said v2.6 and PyTorch/CuPy continuation. | Updated status and partner examples to v2.10 CuPy/Numba. |
| `docs/tutorials/README.md` | Tutorial index still listed PyTorch as a current partner and blocked arbitrary PyTorch/CuPy/Numba wording. | Reworded to NumPy/CuPy/Numba current tutorial guidance. |
| `docs/tutorials/db_workloads.md` | DB tutorial used older-work phrasing for archived correctness anchors. | Reworded to archived work and archive goal-named tests. |
| `docs/tutorials/partner_anyhit.md` | Partner any-hit tutorial still told users to run `torch-cuda`. | Removed the `torch-cuda` command and narrowed the current CUDA path to CuPy. |
| `docs/tutorials/partner_optix_column_anyhit.md` | OptiX partner-column tutorial still described PyTorch/CuPy tensors and continuation. | Reworded to CuPy-owned arrays and CuPy continuation for the current tutorial path. |
| `docs/tutorials/v2_app_building.md` | App-building tutorial still listed PyTorch and a `torch-cuda` command. | Removed PyTorch from the current partner layer and command examples. |
| `docs/vision.md` | Vision page used "old" release evidence wording. | Reworded to archived release evidence and archived milestones. |
| `examples/v2_0/README.md` | Examples index needed v2.10 alignment. | Updated learner-facing status to v2.10. |
| `examples/v2_0/getting_started/README.md` | Getting-started index needed v2.10 alignment. | Updated learner-facing status to v2.10. |
| `examples/v2_0/research_benchmarks/barnes_hut/README.md` | Barnes-Hut benchmark README still advertised Torch in the current partner exact-force row. | Reworded to CuPy or Numba. |
| `examples/v2_0/research_benchmarks/raydb_style/README.md` | RayDB README still named PyTorch CUDA tensors, Torch/CuPy columns, and Triton continuation as visible current-path prose. | Reworded to generic current CUDA partner columns and archived continuation material. |
| `examples/v2_0/research_benchmarks/rt_dbscan/README.md` | RT-DBSCAN README still said CuPy or PyTorch installed and had an awkward compatibility-name sentence. | Narrowed the current partner run to CuPy and cleaned compatibility wording. |
| `examples/v2_0/research_benchmarks/rtnn/README.md` | RTNN README described a helper as older and called evidence historical. | Reworded helper/evidence language for current benchmark docs. |
| `src/rtdsl/primitive_catalog.py` | Source renderer generated v2.7-specific prose into the current primitive catalog. | Reworded generated catalog text to current discovery/planner language. |
| `src/rtdsl/primitive_discovery.py` | Discovery boundary string still said v2.7. | Reworded to current semantic primitive search. |
| `src/rtdsl/primitive_planner.py` | Planner claim-boundary string still said v2.7. | Reworded to current primitive advisory plans. |
| `tests/goal4271_v2_10_user_doc_cleanup_test.py` | No guard existed for stale current-doc wording or dead local links. | Added regression tests for stale current-doc terms, current-doc links/anchors, and v2.10 key entrypoints. |

## Files Checked And Left Unchanged

| File | Status | Explanation |
| --- | --- | --- |
| `docs/features/lsi/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/overlay/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/pip/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/point_nearest_segment/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/polygon_pair_overlap_area_rows/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/polygon_set_jaccard/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/ray_tri_anyhit/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/ray_tri_hitcount/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/reduce_rows/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/segment_polygon_anyhit_rows/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/segment_polygon_hitcount/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/features/visibility_rows/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/learn/benchmark_partner_reference_matrix.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/learn/partner_choice_for_custom_logic.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/learn/prepared_execution_pattern.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/learn/prepared_session_reuse.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/learn/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/embree_baseline_contracts.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/embree_evaluation_matrix.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/rayjoin_datasets.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/rayjoin_paper_dataset_provenance.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/rayjoin_paper_reproduction_checklist.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/rayjoin_paper_reproduction_matrix.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/rayjoin_public_dataset_sources.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/research/rayjoin/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/rtdl/llm_authoring_guide.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/rtdl/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/rtdl/workload_cookbook.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/feature_quickstart_cookbook.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/graph_workloads.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/hello_world.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/nearest_neighbor_workloads.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/rendering_and_visual_demos.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/segment_polygon_workloads.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `docs/tutorials/sorting_demo.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/apps/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/features/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/learner_apps/gpu_rmq/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/learner_apps/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/partners/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/contact_manifold/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/librts_spatial_index/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/robot_collision/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |
| `examples/v2_0/research_benchmarks/triangle_counting/README.md` | checked | No stale current-surface terms or broken local links found; left unchanged. |

## Notes

- The directory name `examples/v2_0/` remains unchanged because it is a stable
  repository path, not learner-facing version guidance.
- Report, review, handoff, release-report, history, and audit files remain
  intentionally historical. They are excluded from the current-doc stale-term
  gate so the project does not rewrite evidence history.
- The cleanup does not claim package-install support, broad speedup, automatic
  partner selection, or true zero-copy.
