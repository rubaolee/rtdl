# V4 Iron Rule Audit: User-Visible Files And Linux Clone

Date: 2026-06-27

Release under test: `v4.0.0`

Release commit under test: `862b9b7049845cbdbb2fc9af9afa0b4b1a4a8501`

## Iron Rules

1. Re-audit every user-visible file and record whether it is in the best state.
2. Clone the release on local Linux as a simulated user, learn from the public path, and run the public code. Any violation forces a fix and a rerun.

## Result

Status: `clear_after_fix_and_rerun`

The audit found one non-best-state issue before final clearance: large benchmark support implementation files and the archive runner lived under `examples/benchmark_apps/_support/`, which is browseable from GitHub. Even though they were not linked as first-time learning files, that was not the best possible user-visible state. The fix moved the large support implementation into `src/rtdsl/_example_support/`, kept only thin shims in `examples/benchmark_apps/_support/`, added `_repo_bootstrap.py` so examples run without manual `PYTHONPATH`, and expanded public scanning from selected entrypoints to all tracked files under `examples/simple/`, `examples/benchmark_apps/`, and `examples/paper_reproduction/`.

## Local Verification After Fix

Windows/local repository:

- `py -3 scripts\v4_universe_audit.py --strict-release`: `status = pass`; `public_file_count = 83`; `public_findings = []`; `public_link_findings = []`; `unknown_untracked_count = 0`.
- Public docs/frontdoor/wording tests: `Ran 30 tests ... OK`.
- Release staging/clean checkout tests: `Ran 9 tests ... OK`.
- `py -3 scripts\v4_release_clean_checkout_gate.py`: `status = passed`; `tag_matches_head = true`; `working_tree_clean = true`.

Local Linux simulated user clone (`ssh 192.168.1.20`):

- Clone path: `/tmp/rtdl_v4_user_clone_20260627_184033`
- Command: `git clone --depth 1 --branch v4.0.0 https://github.com/rubaolee/rtdl.git`
- Checked out commit: `862b9b7049845cbdbb2fc9af9afa0b4b1a4a8501`
- Tag at HEAD: `v4.0.0`
- Git status after clone: clean
- Python: `Python 3.12.3`
- Ran quickstart: `examples/simple/v4_frontdoor_quickstart.py`
- Ran learning recipe: `examples/simple/benchmark_app_recipes.py`
- Ran callback boundary examples: `operator_callback_planning.py --case complex-callback`, `custom_predicate_early_exit_planning.py`
- Ran dry-run device-array example: `fixed_radius_torch_device_arrays.py --dry-run --copies 2`
- Ran all 10 benchmark `v4_app.py --json` entrypoints and JSON validation
- Ran `v4_app.py --run-harness -- --help` bridge smoke
- Ran `examples/paper_reproduction/rayjoin.py --help` bridge smoke
- Ran `scripts/v4_universe_audit.py --strict-release`: `status = pass`; `public_file_count = 83`; no public findings; no unknown untracked files
- Ran public docs/frontdoor/wording unittest group: `Ran 30 tests ... OK`

## User-Visible File Audit Table

| File | Role | Should Be User-Visible Here? | Content Correct? | Historical/Internal Leak? | Best-State Reflection | Required Action |
| --- | --- | --- | --- | --- | --- | --- |
| `README.md` | root entrypoint | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/README.md` | public documentation | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/app_level_benchmark_summary.md` | public documentation | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/current_v4_status.md` | public documentation | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/learn/README.md` | learning reference | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/learn/operator_catalog.md` | learning reference | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/learn/partner_choice.md` | learning reference | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/learn/performance_wording.md` | learning reference | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/learn/source_tree_doctor.md` | learning reference | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/public_documentation_map.md` | public documentation | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/v4_engineering_summary.md` | public documentation | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `docs/v4_release_notes.md` | public documentation | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `examples/README.md` | examples index | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `examples/__init__.py` | examples index | Yes | Pass | No | Best current state: visible support file is minimal and clean. | None |
| `examples/benchmark_apps/README.md` | benchmark app support artifact | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `examples/benchmark_apps/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/_support/__init__.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/_support/_repo_bootstrap.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/_support/rtdl_ann_candidate_app.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/_support/rtdl_barnes_hut_force_app.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/_support/rtdl_graph_triangle_count.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/_support/rtdl_language_reference.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/_support/v4_public_entry.py` | thin benchmark support shim/entry helper | Yes | Pass | No | Clear after fix: visible support layer is now thin; large implementation and archive paths are outside the examples browsing path. | None |
| `examples/benchmark_apps/barnes_hut/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/barnes_hut/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/contact_manifold/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/contact_manifold/cpp_contact_witness_baseline.cpp` | benchmark app support artifact | Yes | Pass | No | Best current state: visible support file is minimal and clean. | None |
| `examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/contact_manifold/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/hausdorff_xhd/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_function.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/hausdorff_xhd/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/librts_spatial_index/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/librts_spatial_index/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/raydb_style/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/raydb_style/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/robot_collision/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/robot_collision/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/rt_dbscan/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/rt_dbscan/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/rtnn/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/rtnn/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/spatial_rayjoin/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/spatial_rayjoin/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/benchmark_apps/triangle_counting/__init__.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/triangle_counting/rt_graph_contract.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | compatibility bridge | Yes | Pass | No | Acceptable best state: compatibility bridge only; preserves old commands without exposing full legacy harness bodies. | None |
| `examples/benchmark_apps/triangle_counting/v4_app.py` | benchmark app V4 entrypoint | Yes | Pass | No | Best current state: short V4 entrypoint only; users start here. | None |
| `examples/paper_reproduction/README.md` | paper reproduction entrypoint/doc | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `examples/paper_reproduction/rayjoin.py` | paper reproduction entrypoint/doc | Yes | Pass | No | Best current state: visible support file is minimal and clean. | None |
| `examples/paper_reproduction/rt_barneshut.py` | paper reproduction entrypoint/doc | Yes | Pass | No | Best current state: visible support file is minimal and clean. | None |
| `examples/simple/README.md` | simple runnable example | Yes | Pass | No | Best current state: user-facing current V4 wording; no internal review/process language; links checked. | None |
| `examples/simple/__init__.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/aabb_index_all_ops_count.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/benchmark_app_recipes.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/closest_hit_grouped_argmin_torch_device_arrays.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/custom_predicate_early_exit_planning.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/fixed_radius_torch_device_arrays.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/operator_callback_planning.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/point_group_nearest_witness_torch_device_arrays.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/primitive_grouped_i64_reduction_torch_device_arrays.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/ray_triangle_any_hit_flags_torch_device_arrays.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `examples/simple/v4_frontdoor_quickstart.py` | simple runnable example | Yes | Pass | No | Best current state: runnable learner example; covered by public tests or dry-run smoke. | None |
| `tutorials/README.md` | tutorial index | Yes | Pass | No | Best current state: visible support file is minimal and clean. | None |
| `tutorials/current/01_first_run.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/02_hello_world.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/03_backend_choice.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/04_prepared_runtime.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/05_measurement_boundaries.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/06_benchmark_apps.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/07_partner_choice.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |
| `tutorials/current/README.md` | step tutorial | Yes | Pass | No | Best current state: current V4 learning path; snippets are copy-paste tested. | None |

## Final Judgment

Every file in the current public user path has been rechecked. The originally found support-layer flaw was fixed and the stricter gates now cover 83 user-visible files rather than the previous narrower entrypoint set. The local Linux clone passed the simulated user path. Current status is clear.
