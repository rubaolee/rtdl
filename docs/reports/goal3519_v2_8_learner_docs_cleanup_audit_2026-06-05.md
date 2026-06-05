# Goal3519: v2.8 Learner Docs And Research Benchmark Cleanup Audit

Date: 2026-06-05

Status: internal docs cleanup; not release authorization.

## Purpose

Goal3519 cleans the active learner-facing docs after the v2.8 prepared-execution and benchmark-matrix work. The rule is simple: normal users should see one coherent current v2.8 story. Historical release packages, old reports, and old reviews remain available in history/report paths, but they should not interrupt the main learning path.

This audit covers the front page, docs index, learner docs, tutorial ladder, and research benchmark README files. It does not rewrite historical reports or archived release records.

## Summary

| Area | Old problem | Action | Residual boundary |
| --- | --- | --- | --- |
| Front page | Taught v2.6 as the current released surface | Reframed as current v2.8 source-tree surface with prepared execution and Goal3518 matrix | Historical v2.6/v2.3 links remain only in the history/audit section |
| Docs index | Described Learn as v2.6 and listed a current v2.6 release package | Reframed Learn as v2.8, changed current reference to Goal3518 matrix, changed release-report description to archived evidence | Release reports remain accessible for auditors |
| Learner docs | Partner guidance still mentioned v2.6 and the old v2.6 helper | Updated to v2.8 guidance and pointed programmatic guidance to `v2_8_benchmark_matrix()` | Older helper names may still exist in code for compatibility; they are not taught as the current learner path |
| Tutorials | Tutorial ladder and per-workload pages said v2.x/v2.6/release package | Updated current tutorial wording to v2.8 and benchmark-matrix framing | Tutorial scripts still live under stable historical `examples/v2_0` paths |
| Research benchmarks | README files used v2.x/v2.6 labels for active studies | Updated top benchmark index plus Hausdorff, RayJoin, RayDB, and RT-DBSCAN READMEs to v2.8/current wording | Paper-reproduction and public-speedup boundaries remain blocked |

## File-By-File Audit

| File | Status before | Action taken | Explanation |
| --- | --- | --- | --- |
| `README.md` | Said docs were for v2.6 released surface and had a `v2.6 Release` section | Changed to current v2.8 source-tree surface, added prepared execution and Goal3518 matrix context, renamed historical release links | The front page now teaches the current branch without turning v2.8 into a package-install or public-speedup promise |
| `docs/README.md` | Learn door, current status, current reference table, directory map, and rule still described v2.6/release package wording | Updated to current v2.8 boundaries, Goal3518 matrix, and archived release evidence wording | Keeps current docs clean while preserving audit/release-report paths |
| `docs/learn/benchmark_partner_reference_matrix.md` | Status said v2.6 and final paragraph pointed to `plan_v2_6_partner_choice(...)` | Updated status to v2.8 and programmatic guidance to `v2_8_benchmark_matrix()` / `summarize_v2_8_benchmark_matrix()` | Learners now see the new matrix source-of-truth instead of old helper naming |
| `docs/learn/partner_choice_for_custom_logic.md` | Status and Numba guidance said v2.6; example used old v2.6 helper | Updated to v2.8 and replaced example with `v2_8_benchmark_matrix()` metadata iteration | Preserves explicit user partner choice and no auto-selection |
| `docs/learn/primitive_discovery_workflow.md` | Status said v2.7 source-tree workflow | Updated to current v2.8 source-tree discovery workflow | Primitive discovery is now part of the current learner story |
| `docs/tutorials/README.md` | Title and claim boundary taught v2.x/v2.6/v2.7 as mixed current surfaces | Updated title and tutorial path to v2.8; primitive discovery and prepared execution are current guidance | Removes multi-version clutter from the tutorial door |
| `docs/tutorials/db_workloads.md` | Said v2.x and referenced v2.6 partner-choice guide | Updated to v2.8 and current partner-choice guide | Database tutorial now follows current single-version language |
| `docs/tutorials/graph_workloads.md` | Said v2.x-facing | Updated to v2.8-facing | Wording-only cleanup |
| `docs/tutorials/hello_world.md` | Said v2.x-facing | Updated to v2.8-facing | Wording-only cleanup |
| `docs/tutorials/nearest_neighbor_workloads.md` | Said v2.x-facing and "release package" | Updated to v2.8-facing and benchmark-matrix wording | Avoids teaching release-package history in the current tutorial |
| `docs/tutorials/partner_anyhit.md` | Said v2.x-facing | Updated to v2.8-facing | Wording-only cleanup |
| `docs/tutorials/partner_optix_column_anyhit.md` | Said v2.x OptiX partner-column idea | Updated to v2.8 OptiX partner-column idea | Wording-only cleanup |
| `docs/tutorials/rendering_and_visual_demos.md` | Said v2.x-facing | Updated to v2.8-facing | Wording-only cleanup |
| `docs/tutorials/segment_polygon_workloads.md` | Said v2.x-facing and used released-package/host-indexed wording | Updated to v2.8-facing, current source-tree wording, and v2.8 app-building link text | Keeps segment/polygon docs current while avoiding release claims |
| `docs/tutorials/sorting_demo.md` | Said v2.x-facing | Updated to v2.8-facing | Wording-only cleanup |
| `docs/tutorials/v2_app_building.md` | Title and text said v2.x/v2.6/release package | Updated to v2.8 app building and Goal3518 benchmark matrix wording | The filename remains stable for links, but the visible tutorial is current |
| `examples/v2_0/research_benchmarks/README.md` | Top-level benchmark index said v2.x and v2.6 custom-kernel lane | Updated to v2.8 and prepared-execution guidance | Directory path remains `v2_0` for compatibility; README explains current behavior |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md` | Said v2.x user/program in several learner-facing lines | Updated to v2.8 wording | Keeps Hausdorff benchmark current without changing method names |
| `examples/v2_0/research_benchmarks/raydb_style/README.md` | Said not recommended v2.6 path and current v2.6 recommendation | Updated to current/v2.8 recommendation | Maintains primitive-first RayDB boundary and paused Triton conclusion |
| `examples/v2_0/research_benchmarks/rt_dbscan/README.md` | Said current v2.x benchmark-app scope | Updated to current v2.8 benchmark-app scope | Wording-only cleanup |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | Said v2.x user/expression and v2.x claim boundary | Updated to v2.8 user/expression and v2.8 claim boundary | Keeps RayJoin paper-reproduction boundary blocked |
| `tests/goal3519_v2_8_learner_docs_cleanup_test.py` | No guard existed | Added active-doc stale-term and local-link checks | Prevents the learner path from drifting back to v2.6/v2.x wording |

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3519_v2_8_learner_docs_cleanup_test

Ran 3 tests in 0.096s
OK
```

Additional scan:

```text
rg -n "v2\\.6|v2\\.7|v2\\.x|v2_6|v2_7|v2\\.5|v2\\.3|release package" \
  docs/README.md docs/learn docs/tutorials examples/v2_0/research_benchmarks/README.md
```

No matches were found in the active docs scanned above. The root `README.md` still contains historical links to v2.6 and v2.3 release packages inside the explicit "History And Audit Trail" section; that is intentional.

## Residual Risk

Some example Python files still contain legacy internal names such as `v2_6` in compatibility helpers. This Goal3519 cleanup does not rename code APIs. Goal3520's stale-doc and claim-boundary audit should decide whether those names need aliases, quarantine notes, or code migration before final v2.8 internal closeout.

## Verdict

`accept-with-boundary`

The active learner-facing docs now present one v2.8 story. This is not a release packet and does not authorize public speedup, broad RT-core, true-zero-copy, package-install, paper-reproduction, hidden partner selection, or app-specific engine claims.
