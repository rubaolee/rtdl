# V4 User-Visible File Audit From README

Date: 2026-06-27

Scope: files a user can reasonably reach from the project README through the
current docs, tutorials, examples, benchmark-app examples, and
paper-reproduction examples.

Excluded from this audit: `src/`, `tests/`, `scripts/`, `future/`, `history/`,
and untracked local caches such as `__pycache__/`.

Questions answered for every file:

1. Should this file be in the current user-visible path?
2. Is the content correct for V4.0.0?
3. Does it contain historical, internal, or misleading information?
4. What remediation is recommended?

## Overall Verdict

The front-door documents, tutorials, simple examples, and README files are now
mostly clean and coherent. A first cleanup step has also added clean
`v4_app.py` wrappers for all 10 benchmark apps and changed the benchmark README
and tutorial path to point at those wrappers instead of the old full harnesses.

The remaining problem is source browsing inside `examples/benchmark_apps/`:
several full benchmark harnesses still expose internal goal names, old
evidence/report paths, V2/V3-era helper names, and release-defense wording
inside source code or emitted metadata. These files are no longer the README
entrypoints, but they are still present in the public tree as implementation
harnesses.

## Recommended Release Fix Strategy

1. Keep the current docs/tutorials/simple examples and benchmark `v4_app.py`
   wrappers as the primary learning path.
2. For remaining full benchmark harnesses, choose one of two approaches:
   - scrub the existing harness sources to remove `Goal...`, old report paths,
     internal evidence labels, and confusing V2/V3 helper names; or
   - move full historical harnesses behind `_legacy/` or `history/` while
     keeping the clean current V4 wrappers under `examples/benchmark_apps/`.
3. Treat full harness files with `FIX_BEFORE_PUBLIC_PUSH` as blockers if source browsing on
   GitHub is considered part of the user experience.

## Per-File Audit Table

| File | Should be here? | Content correct? | Historical/error info? | Remediation |
| --- | --- | --- | --- | --- |
| `README.md` | Yes, primary front door. | Correct current V4 positioning. | Only valid V2/V3 comparison context; no stale link found. | Keep. |
| `docs/README.md` | Yes, docs index. | Correct and short. | No improper historical leak. | Keep. |
| `docs/v4_release_notes.md` | Yes, release notes. | Correct bounded release summary. | V2/V3 mentions are comparison context. | Keep. |
| `docs/current_v4_status.md` | Yes, current status page. | Correct current feature/performance snapshot. | V2/V3 mentions are explicit compatibility/performance context. | Keep. |
| `docs/app_level_benchmark_summary.md` | Yes, benchmark report. | Correct as user-facing matrix summary. | No internal review language found; comparison context remains. | Keep; update only if new benchmark evidence changes. |
| `docs/public_documentation_map.md` | Yes, public path map. | Correct current path. | No archive/history link remains. | Keep. |
| `docs/v4_engineering_summary.md` | Yes, maintainer-readable but still public. | Correct compact architecture summary. | No internal process leak; now links to project README correctly. | Keep. |
| `docs/learn/README.md` | Yes, learn index. | Correct. | None found. | Keep. |
| `docs/learn/operator_catalog.md` | Yes, operator reference. | Correct measured-surface catalog. | V2/V3 comparison text is denominator context. | Keep; update with future promoted surfaces only after evidence. |
| `docs/learn/partner_choice.md` | Yes, user guide. | Correct partner-choice guidance. | None found. | Keep. |
| `docs/learn/performance_wording.md` | Yes, performance reading guide. | Correct and useful for users. | V2/V3 mentions are necessary denominator context. | Keep. |
| `docs/learn/source_tree_doctor.md` | Yes, local checkout helper. | Correct. | None found. | Keep. |
| `tutorials/README.md` | Yes, tutorial entrypoint. | Correct. | None found. | Keep. |
| `tutorials/current/README.md` | Yes, lesson index. | Correct learning progression. | None found. | Keep. |
| `tutorials/current/01_first_run.md` | Yes. | Correct intro to RT-shaped relations. | None found. | Keep. |
| `tutorials/current/02_hello_world.md` | Yes. | Correct simple first program. | None found. | Keep. |
| `tutorials/current/03_backend_choice.md` | Yes. | Correct backend/operator-planning lesson. | None found. | Keep. |
| `tutorials/current/04_prepared_runtime.md` | Yes. | Correct prepared-runner concept lesson. | None found. | Keep. |
| `tutorials/current/05_measurement_boundaries.md` | Yes. | Correct user-level performance measurement lesson. | None found. | Keep. |
| `tutorials/current/06_benchmark_apps.md` | Yes, bridge to benchmark apps. | Correct as a learning bridge; now points to `v4_app.py` wrappers. | No internal review wording found. | Keep synchronized with wrapper names. |
| `tutorials/current/07_partner_choice.md` | Yes. | Correct partner decision lesson. | None found. | Keep. |
| `examples/README.md` | Yes, examples index. | Correct three-entry layout. | No old examples/archive link remains. | Keep. |
| `examples/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/simple/README.md` | Yes. | Correct runnable example index. | None found. | Keep. |
| `examples/simple/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/simple/v4_frontdoor_quickstart.py` | Yes. | Correct quickstart payload. | None found. | Keep. |
| `examples/simple/benchmark_app_recipes.py` | Yes. | Correct human-readable recipe script. | Mentions V2/V3 only indirectly through V4 plans where appropriate. | Keep. |
| `examples/simple/operator_callback_planning.py` | Yes. | Correct callback-boundary example. | None found. | Keep. |
| `examples/simple/custom_predicate_early_exit_planning.py` | Yes. | Correct constrained Numba predicate planning example. | V2/V3 ratio fields are evidence context in output. | Keep. |
| `examples/simple/fixed_radius_torch_device_arrays.py` | Yes. | Correct dry-run/device-array example. | None improper; threshold terms are domain terms. | Keep. |
| `examples/simple/closest_hit_grouped_argmin_torch_device_arrays.py` | Yes. | Correct dry-run/device-array example. | None found. | Keep. |
| `examples/simple/ray_triangle_any_hit_flags_torch_device_arrays.py` | Yes. | Correct dry-run/device-array example. | None found. | Keep. |
| `examples/simple/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Yes. | Correct dry-run/device-array example. | None found. | Keep. |
| `examples/simple/primitive_grouped_i64_reduction_torch_device_arrays.py` | Yes. | Correct dry-run/device-array example. | None found. | Keep. |
| `examples/simple/point_group_nearest_witness_torch_device_arrays.py` | Yes. | Correct dry-run/device-array example. | None found. | Keep. |
| `examples/simple/aabb_index_all_ops_count.py` | Yes. | Correct dry-run/native-runner example. | None found. | Keep. |
| `examples/benchmark_apps/README.md` | Yes. | Correct index; now points to clean `v4_app.py` wrappers. | No process leak in README itself. | Keep. |
| `examples/benchmark_apps/_support/v4_public_entry.py` | Yes as shared wrapper support. | Correct clean V4 wrapper metadata and harness delegation. | No internal goal/review leak found. | Keep; keep it in public scan. |
| `examples/benchmark_apps/rt_dbscan/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/rtnn/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/triangle_counting/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/robot_collision/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/raydb_style/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/librts_spatial_index/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/contact_manifold/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/spatial_rayjoin/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/barnes_hut/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/hausdorff_xhd/v4_app.py` | Yes as clean current app entry. | Correct wrapper. | None found. | Keep. |
| `examples/benchmark_apps/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/_support/__init__.py` | Yes as private support marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/_support/rtdl_language_reference.py` | Yes as support reference. | Correct clean eDSL reference snippets. | None found. | Keep. |
| `examples/benchmark_apps/_support/rtdl_graph_triangle_count.py` | Yes as support helper. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/_support/rtdl_ann_candidate_app.py` | Yes as RTNN support helper. | Correct. | No internal goal leak found. | Keep; consider documenting it as support-only. |
| `examples/benchmark_apps/_support/rtdl_barnes_hut_force_app.py` | Yes as Barnes-Hut support helper. | Mostly correct. | Contains older backend names and benchmark support details; not harmful but not beginner-facing. | Keep under `_support`; avoid linking directly. |
| `examples/benchmark_apps/barnes_hut/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | Yes as benchmark app, but not clean public source yet. | Functionally important. | Contains V2.8/Phoenix/V3 metadata, old scorecard/source paths, and internal release-claim fields. | `FIX_BEFORE_PUBLIC_PUSH`: scrub metadata or expose a clean V4 wrapper and move old harness internals behind support/history. |
| `examples/benchmark_apps/contact_manifold/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/contact_manifold/cpp_contact_witness_baseline.cpp` | Yes as local baseline helper. | Correct. | None found. | Keep; README should mention it is a baseline helper if users compile it. |
| `examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | Yes as benchmark app, but not clean public source yet. | Functionally important. | Uses `goal2621` build path and older primitive naming/metadata. | `FIX_BEFORE_PUBLIC_PUSH`: rename goal build artifact and scrub internal metadata labels. |
| `examples/benchmark_apps/hausdorff_xhd/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | Yes as current Hausdorff app. | Correct current app entrypoint. | Contains comparison-era naming but no internal goal leak found. | Keep; make it the only public Hausdorff entrypoint after helper cleanup. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_function.py` | Questionable in current public path. | Useful historical/helper code. | Filename and API are explicitly V2-era. | `MOVE_OR_WRAP`: move under support/history or rename as compatibility helper not public tutorial source. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py` | No, not as current user-facing app source. | Useful lab material, not current app. | Explicit V2 lab framing. | `MOVE_OR_WRAP`: archive or hide under `_support` with current wrapper. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py` | No, not as current user-facing app source. | Useful compatibility benchmark. | Explicit V2 user-benchmark framing. | `MOVE_OR_WRAP`: archive or hide under `_support`; keep current entrypoint clean. |
| `examples/benchmark_apps/librts_spatial_index/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | Yes as benchmark app, but wording needs cleanup. | Functionally useful. | Contains claim-boundary/reproduction wording that reads like release defense. | `FIX_BEFORE_PUBLIC_PUSH`: rewrite source metadata as user-facing scope notes. |
| `examples/benchmark_apps/raydb_style/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py` | Yes as benchmark app, but not clean public source yet. | Functionally important. | Contains `v4_goal...`, Goal text, many V2.4/V2.5 route labels, "does not authorize" wording, and review/evidence notes. | `FIX_BEFORE_PUBLIC_PUSH`: expose clean current app wrapper or scrub internal labels from emitted metadata. |
| `examples/benchmark_apps/robot_collision/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py` | Yes as benchmark app, but not clean public source yet. | Functionally important. | Contains many Goal labels and internal evidence/status fields. | `FIX_BEFORE_PUBLIC_PUSH`: remove Goal labels from comments, defaults, and JSON metadata; rename build/evidence fields. |
| `examples/benchmark_apps/rt_dbscan/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | Yes as benchmark app, but not clean public source yet. | Functionally important. | Heavy internal history: many Goal refs, policy evidence refs, mixed predicate promotion notes, and old route labels. | `FIX_BEFORE_PUBLIC_PUSH`: create clean V4-facing app wrapper or scrub historical policy/evidence data from public source. |
| `examples/benchmark_apps/rtnn/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py` | Yes as benchmark app, but not clean public source yet. | Functionally important. | Links to old `docs/reports/goal...` paths and imports goal-named script runners. | `FIX_BEFORE_PUBLIC_PUSH`: move old runner bridge behind support API and remove report-path metadata from public output. |
| `examples/benchmark_apps/spatial_rayjoin/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Yes as RayJoin app, but path/name are confusing for V4 users. | Functionally important. | Filename says V2; imports V3 accounting helpers; contains a Goal comment. | `FIX_BEFORE_PUBLIC_PUSH`: add clean V4-named wrapper and make README point to it; move old V2-named implementation behind support/history. |
| `examples/benchmark_apps/triangle_counting/__init__.py` | Yes as package marker. | Correct. | None found. | Keep. |
| `examples/benchmark_apps/triangle_counting/rt_graph_contract.py` | Yes as support contract. | Correct. | Some V2-era naming exists as implementation detail. | Keep under app folder; consider `_support` move if cleaning user source tree strictly. |
| `examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | Yes as benchmark app, but not fully clean source yet. | Functionally important and high-value app. | Contains old report paths and V2.4 primitive constants. | `FIX_BEFORE_PUBLIC_PUSH`: remove old report refs and rename primitive constants to current generic names. |
| `examples/paper_reproduction/README.md` | Yes, separate paper-oriented entrypoint. | Correct. | No improper history; paper distinction is useful. | Keep. |
| `examples/paper_reproduction/rayjoin.py` | Yes as paper wrapper. | Correct wrapper. | Target filename still contains `v2`, which is confusing downstream. | Keep for now; update target after RayJoin wrapper cleanup. |
| `examples/paper_reproduction/rt_barneshut.py` | Yes as paper wrapper. | Correct wrapper. | None found. | Keep. |

## Blocking Findings

1. The benchmark app README/tutorial entrypoints now use clean `v4_app.py`
   wrappers. This fixes the immediate user-entry problem.
2. The remaining `examples/benchmark_apps/` issue is deeper source browsing:
   full harness files still expose internal development history in several
   implementation files.
3. The docs/tutorials/simple examples are substantially clean and should not be
   churned again unless a specific stale statement is found.
4. The cleanest next engineering action is not another docs rewrite; it is a
   benchmark-app source cleanup pass:
   - remove Goal/report/review/evidence labels from public source and emitted
     JSON;
   - rename or wrap V2/V3-named app files;
   - keep legacy compatibility internals under `_support` or `history/`;
   - keep benchmark app README pointing only to clean current wrappers.

## Verification Commands Used

```powershell
rg --files README.md docs tutorials examples
rg -n "Goal\d+|goal\d+|review debt|Claude|Gemini|Antigravity|parity/control|release candidate|future/v4|docs/reviews|history/|history\\|examples/current|docs/current|file:///|TODO|FIXME|not a release|development surface|development guidance" README.md docs tutorials examples
rg -n "\bv2\b|v2_|V2|\bv3\b|v3_|V3|old|legacy|archive|report|evidence|claim boundary|not authorize|does not authorize|internal|audit|review|candidate" README.md docs tutorials examples
```

Machine gate status before this audit file was added:

- `scripts\v4_universe_audit.py`: `public_findings: []`, `public_link_findings: []`
- public/frontdoor tests: `Ran 34 tests ... OK`
- `scripts\v4_release_clean_checkout_gate.py`: passed

This audit intentionally widens the lens beyond the current machine gate by
treating full benchmark-app source browsing as user-visible.
