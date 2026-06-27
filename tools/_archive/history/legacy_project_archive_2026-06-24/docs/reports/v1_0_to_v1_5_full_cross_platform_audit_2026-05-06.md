# RTDL v1.0 to v1.5 Full Cross-Platform Audit

Date: 2026-05-06

## Verdict

RTDL v1.5 is a major scoped release jump from v1.0: it establishes the
standalone Embree+OptiX language/runtime surface for the supported v1.5
contracts, adds stable generic traversal-plus-reduction primitives, records
same-contract correctness and benchmark evidence for 14 included app contracts,
and explicitly excludes 4 rows from the standalone-complete claim.

The release claim is acceptable only within the published v1.5 boundary:
source-tree usage, active Embree+OptiX support, no package-install claim, no
whole-app speedup claim, no `COLLECT_K_BOUNDED` stabilization, and no claim
that native engines are fully app-agnostic internally.

Cross-platform audit result:

- Windows supported v1.5/public slice: pass.
- Linux supported v1.5/public slice: pass.
- Windows Embree baseline/evaluation slice: pass.
- Linux Embree baseline/evaluation slice: conditional pass in the local dirty
  working tree only, after the post-tag LSI boundary-intersection fix described
  below. The released `v1.5` tag and current GitHub `origin/main` do not contain
  that fix.
- Full discovery is not green on either Windows or Linux because historical,
  pod-artifact, macOS-only, and absolute-path tests remain in the repository.
  Those failures are outside the supported v1.5 release slice but should be
  triaged if the project wants one-command full-suite green on common OSes.

## Scope

This audit compares released `v1.0` to released `v1.5` and then checks current
`main` plus the local Windows/Linux validation state.

Tag and checkout facts:

- `v1.0` commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- `v1.5` annotated tag target: `2d64508835dde05427ab10727c21b29977dfdfd7`
- Current `main` during this audit: `a5de1af441cfea41843feb435c603e8a3057188b`
- Current describe before local report creation: `v1.5-3-ga5de1af4-dirty`
- `VERSION`: `v1.5`

Diff scale from `v1.0` to `v1.5`:

- 269 commits
- 809 changed files
- 207,919 insertions
- 821 deletions

Current `main` is three commits after the `v1.5` tag. Those commits record
publish/docs follow-up and do not move the `v1.5` or `v1.0` tags.

## What Changed

The main functional movement from v1.0 to v1.5 is not a new whole-application
speedup promise. It is a language/runtime surface consolidation:

- Stable primitive set for the supported v1.5 surface:
  `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
  `REDUCE_INT(COUNT|SUM)`.
- Generic primitive modules and contracts were added, including generic
  traversal/count/reduction paths, primitive contract schema/registry, grouped
  reductions, float reductions, DB/polygon/graph primitive wrappers, and
  support-maturity/readiness validators.
- Active standalone backends are Embree and OptiX.
- Vulkan, HIPRT, and Apple RT are frozen proof surfaces before v2.1.
- `COLLECT_K_BOUNDED` remains experimental and is deferred to v1.5.1.
- Native engines are not yet app-agnostic internally; v1.5 only claims
  app-name-free stable primitive paths where documented.

## Included Surface

v1.5 includes 14 app contracts:

- `database_analytics`
- `graph_analytics`
- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `polygon_pair_overlap_area_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`
- `barnes_hut_force_app`

v1.5 excludes 4 rows from the standalone-complete claim:

- `segment_polygon_anyhit_rows`
- `polygon_set_jaccard`
- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

The exclusion reasons are explicit: row-returning `COLLECT_K_BOUNDED` is
deferred to v1.5.1, while Apple RT and HIPRT are frozen before v2.1.

## Evidence Reviewed

Primary release-package evidence:

- `docs/release_reports/v1_5/README.md`
- `docs/release_reports/v1_5/release_statement.md`
- `docs/release_reports/v1_5/support_matrix.md`
- `docs/release_reports/v1_5/audit_report.md`
- `docs/release_reports/v1_5/tag_preparation.md`

Primary gate evidence:

- `docs/reports/goal1400_v1_5_standalone_app_classification_2026-05-06.md`
- `docs/reports/goal1402_v1_5_pending_app_correctness_closure_2026-05-06.md`
- `docs/reports/goal1405_v1_5_support_maturity_matrix_2026-05-06.md`
- `docs/reports/goal1406_v1_5_benchmark_evidence_matrix_2026-05-06.md`
- `docs/reports/goal1410_v1_5_vs_v1_0_rtx_pod_perf_results_2026-05-06.md`
- `docs/reports/goal1411_v1_5_boundary_backend_consensus_status_2026-05-06.md`
- `docs/reports/goal1412_v1_5_docs_release_cleanup_consensus_2026-05-06.md`
- `docs/reports/goal1413_app_independent_engine_roadmap_2026-05-06.md`

Existing consensus:

- Goal1411 records Codex + Claude + Antigravity/Gemini acceptance of the v1.5
  native-engine boundary and RTX pod backend/subpath interpretation.
- Goal1412 records docs release-cleanup consensus.
- These consensus artifacts support the published boundary but do not authorize
  new broad speedup claims or future tag movement.

## Cross-Platform Validation

Windows validation was run in:

`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`

Linux validation was run over SSH on `192.168.1.20` in:

`/home/lestat/work/rtdl_v1_5_linux_check`

Windows interpreter note:

- `python` is the Microsoft Store alias on this machine.
- Working Windows interpreter: `py -3`, Python `3.11.9`.

Linux environment note:

- Host: `lx1`
- Python: `/usr/bin/python3`, Python `3.12.3`
- Embree: `libembree4.so.4` present
- Build tools: `make`, `clang++`, and `g++` present

Validated slices:

- Windows v1.5/public slice: `Ran 218 tests ... OK`, run from current
  `main` plus the local dirty Embree LSI fix.
- Linux v1.5/public slice: `Ran 218 tests ... OK`, run from current `main`
  plus the local dirty Embree LSI fix.
- Windows Embree baseline/evaluation slice:
  `tests.baseline_integration_test tests.evaluation_test`, `Ran 7 tests ... OK`,
  run from current `main` plus the local dirty Embree LSI fix.
- Linux Embree baseline/evaluation slice:
  `tests.baseline_integration_test tests.evaluation_test`, `Ran 7 tests ... OK`,
  run from current `main` plus the local dirty Embree LSI fix.
- Windows README examples passed with `py -3`:
  `examples/rtdl_hello_world.py` and
  `examples/rtdl_hausdorff_distance_app.py --backend embree`
- Linux README examples passed with `python3`:
  `examples/rtdl_hello_world.py` and
  `examples/rtdl_hausdorff_distance_app.py --backend embree`

## Post-Tag Finding: Linux Embree LSI Boundary Miss

The broad Linux run found a real Embree correctness issue outside the initial
v1.5/public slice:

- Failing tests before fix:
  `tests.baseline_integration_test` and `tests.evaluation_test`
- Failing dataset:
  `tests/fixtures/rayjoin/br_county_subset.cdb`
- Workload: `lsi`
- CPU rows: one endpoint intersection
- Linux Embree rows before fix: zero
- Windows Embree rows before fix: one matching row

Root cause:

The missed case is an endpoint intersection where the left segment and right
segment share the exact start point. CPU semantics include endpoint
intersections. Linux Embree 4 did not reliably invoke the user-geometry
candidate callback for that boundary case.

Local fix:

- File: `src/native/embree/rtdl_embree_api.cpp`
- Change: pad the Embree LSI candidate ray slightly and add an exact fallback
  only when Embree returns no candidate rows for a probe.
- The exact fallback uses `segment_intersection(...)`; the observed endpoint
  case and the 7-test Embree baseline/evaluation slice are parity-correct after
  the fix.
- The fallback trigger is `query_rows.empty()`. When it fires, it scans all
  right-side segments for that probe, so it is correctness-first and can be
  slower for affected probes. Any future Embree candidate miss that yields an
  empty candidate set would also trigger this exact fallback silently.

Post-fix validation:

- Linux exact case now returns `parity: true`.
- Linux baseline/evaluation: `Ran 7 tests ... OK`.
- Windows baseline/evaluation remains green: `Ran 7 tests ... OK`.
- Windows and Linux v1.5/public slices remain green: `Ran 218 tests ... OK`
  on each platform.

Important boundary:

This fix is currently local working-tree state. It is not part of the released
`v1.5` tag and is not part of GitHub `origin/main` until committed and pushed.
The current dirty working tree does not satisfy the clean-worktree precondition
recorded in the v1.5 tag-preparation document; any future tag or release action
must first commit and verify the fix, then start from a clean tree.

## Full Discovery Status

Full Windows discovery was run before the Linux LSI fix:

- `Ran 2703 tests in 877.078s`
- `FAILED (failures=7, errors=9, skipped=279)`

Full Linux discovery was run before the Linux LSI fix:

- `Ran 2703 tests in 358.555s`
- `FAILED (failures=8, errors=6, skipped=279)`

The Linux LSI failure has now been fixed locally. The remaining full-discovery
blockers are concentrated in historical or platform-sensitive tests:

- hardcoded macOS paths such as `/Users/rl2025/...`
- historical pod artifact/log/archival expectations
- macOS-only Apple RT tests running on non-macOS
- Windows direct execution of `.sh` scripts
- Windows executable-bit assumptions
- older subprocess/path assumptions

These do not invalidate the v1.5 supported-surface claim, but they do mean the
repository cannot yet honestly claim one-command full discovery green on common
Windows/Linux machines.

Full discovery was not rerun after the local LSI fix. Based on the isolated
rerun, the two Linux failures from `baseline_integration_test` and
`evaluation_test` are resolved in the dirty working tree, but the exact
post-fix full-discovery failure count remains unmeasured.

Additional traceability note:

`docs/release_reports/v1_5/release_statement.md` contains some historical
absolute macOS evidence pointers under `/Users/rl2025/...`. Equivalent evidence
files are present repo-relatively under `docs/reports/`, but the absolute paths
are non-portable and should be cleaned up in a follow-up docs traceability pass.

## Claim Boundaries

Allowed v1.5 claims:

- v1.5 is the current public release.
- v1.5 is standalone for the supported Embree+OptiX language/runtime surface.
- v1.5 includes 14 app contracts and excludes 4 rows.
- Stable v1.5 primitives are `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- Source-tree usage remains `PYTHONPATH=src:. python ...`.
- v1.5.1 is the `COLLECT_K_BOUNDED` promotion track.

Disallowed v1.5 claims:

- package-install support
- whole-app speedup
- broad NVIDIA RTX/GPU/backend speedup wording
- stable `COLLECT_K_BOUNDED`
- active Vulkan/HIPRT/Apple RT implementation targets
- fully app-free native-engine internals
- any movement or retagging of `v1.0` or `v1.5`

## Recommendation

Treat v1.5 as release-valid for the documented supported surface, with the
published boundary intact.

Before any next public confidence statement about Windows/Linux readiness,
commit and push the Embree LSI boundary-intersection fix, then rerun:

- Windows v1.5/public slice
- Linux v1.5/public slice
- Windows baseline/evaluation slice
- Linux baseline/evaluation slice

If the project wants stronger cross-platform polish, create a follow-up track
to make full discovery platform-aware:

- skip or guard macOS-only Apple RT tests outside macOS;
- replace hardcoded absolute maintainer paths with repo-relative fixtures or
  explicit skip conditions;
- separate historical pod-intake artifact checks from default discovery;
- run `.sh` tests through Bash/WSL on Windows or skip with a clear reason;
- avoid Unix executable-bit assertions on Windows.
