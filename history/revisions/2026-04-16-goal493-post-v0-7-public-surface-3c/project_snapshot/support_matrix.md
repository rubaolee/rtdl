# RTDL v0.7.0 Support Matrix

Date: 2026-04-16
Status: released bounded DB line

## Workload Surface

Current bounded DB kernels:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Backend Matrix

| Backend | `conjunctive_scan` | `grouped_count` | `grouped_sum` | Notes |
|---|---|---|---|---|
| `cpu_python_reference` | yes | yes | yes | canonical truth path |
| `cpu` | yes | yes | yes | native/oracle correctness path |
| `embree` | yes | yes | yes | native prepared scene reuse; Linux repeated-query perf gate |
| `optix` | yes | yes | yes | native prepared GAS/traversable reuse; Linux GPU validation story |
| `vulkan` | yes | yes | yes | native prepared BLAS/TLAS reuse; Linux GPU validation story |
| `postgresql` | baseline | baseline | baseline | external correctness/perf anchor, not an RTDL backend |

## Query-Shape Boundary

Current bounded DB family supports:

- conjunctive predicates
- up to 3 primary RT clauses per RT job
- one group key
- integer-compatible `grouped_sum`

Current bounded DB family does not support:

- arbitrary SQL
- transactions
- joins as a first-class RTDL DB feature
- multi-group-key grouped RT kernels
- PostgreSQL-style storage, indexing, optimizer behavior, or concurrency

## Prepared Dataset Boundary

Current native prepared DB dataset support:

- `embree`: reusable native scene over encoded row AABBs
- `optix`: reusable custom-primitive GAS/traversable over encoded row AABBs
- `vulkan`: reusable BLAS/TLAS over encoded row AABBs

Current Python API surface:

- `prepare_embree_db_dataset(table_rows, primary_fields=..., transfer="columnar")`
- `prepare_optix_db_dataset(table_rows, primary_fields=..., transfer="columnar")`
- `prepare_vulkan_db_dataset(table_rows, primary_fields=..., transfer="columnar")`

Compatibility path:

- the default remains `transfer="row"` for backward compatibility
- the current performance gate uses `transfer="columnar"`

## Platform Boundary

- `Linux`
  - primary validation platform
  - carries PostgreSQL correctness/performance anchoring
  - carries OptiX and Vulkan validation story
- `Windows`
  - bounded local/runtime surface for non-PostgreSQL work
  - external v0.6 Windows audit found a stale/missing Embree DLL in an older
    snapshot; the release-line loader requires either a matching
    `build/librtdl_embree.dll` from this checkout or first-use rebuild from
    source, and the loader rejects stale DLLs missing required exports
  - Goal 467 fresh release-line sync on `lestat-win` verified `rt.csr_graph`,
    `rt.embree_version()`, `build\librtdl_embree.dll`, all 22 required Embree
    exports, and the public graph Embree examples
- `local macOS`
  - bounded local/runtime surface for non-PostgreSQL work

## Linux Repeated-Query Performance Gate

The current canonical Linux gate uses 200,000 synthetic rows and 10 repeated
queries per workload. It compares RTDL native prepared columnar dataset build
plus repeated queries against the best PostgreSQL modes tested in Goal 451.

| Workload | Backend | Query speedup vs best-tested PG | Total speedup vs best-tested PG |
|---|---:|---:|---:|
| `conjunctive_scan` | Embree | 0.98x | 8.61x |
| `conjunctive_scan` | OptiX | 1.44x | 5.88x |
| `conjunctive_scan` | Vulkan | 1.20x | 6.19x |
| `grouped_count` | Embree | 0.92x | 9.04x |
| `grouped_count` | OptiX | 2.71x | 10.25x |
| `grouped_count` | Vulkan | 1.82x | 9.91x |
| `grouped_sum` | Embree | 1.02x | 7.84x |
| `grouped_sum` | OptiX | 3.08x | 9.84x |
| `grouped_sum` | Vulkan | 2.53x | 9.53x |

Use [Goal 452 RTDL vs best-tested PostgreSQL performance rebase](../../reports/goal452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.md)
for the full table and boundary language. Goal 450 remains historical evidence
against the original single-column indexed PostgreSQL baseline.

## Linux Fresh-Checkout Validation

Goal 464 validates the release package from a clean synced checkout on
`lestat-lx1`:

- `rtdsl` imports from the fresh checkout
- Embree is available immediately
- OptiX and Vulkan become available after fresh-checkout backend builds
- PostgreSQL 16.13 and Python `psycopg2` are available
- focused DB correctness tests pass
- prepared-dataset and columnar-transfer tests pass
- app-level and kernel-form v0.7 DB demos run under `--backend auto`
- all RTDL/PostgreSQL hashes in the measured artifacts match

Use [Goal 464 Linux fresh-checkout validation](../../reports/goal464_v0_7_linux_fresh_checkout_validation_2026-04-16.md)
for the full fresh-checkout evidence package.

Hardware caveat: the Goal 464 Linux GPU is a GTX 1070, which has no NVIDIA RT
cores. That run validates backend functionality and bounded performance on the
current Linux machine, not RT-core hardware acceleration.

## External Tester Response

Goal 467 triaged the two newest external report families:

- macOS user-perspective correctness report:
  - 179/179 checks passed across the public workload surface on available
    backends
- Windows v0.6 audit:
  - older snapshot had stale/missing Embree DLL deployment and stale public API
    exposure
  - the release line now rejects stale/incomplete Embree libraries before use,
    exposes `make build-embree`, and locks `csr_graph`/`validate_csr_graph`
    public exports with regression coverage
  - fresh Windows release-line sync verified the bounded graph/API/Embree
    deployment surface

This does not make Windows the canonical v0.7 DB performance platform.
PostgreSQL and GPU performance validation remain Linux-centered for this release
line.

Goal 471 also preserves a newer external Windows v0.6.1 Expert Attack Suite
report covering BFS, triangle counting, PIP, LSI, resource-pressure cycling, and
randomized parity on Windows Embree. Treat it as positive supporting
graph/geometry stress evidence only; it is not a v0.7 DB/PostgreSQL release
gate and does not authorize staging, tagging, merging, or release.

Goal 477 adds newer local broad unittest discovery evidence. The command
`python3 -m unittest discover -s tests -p '*test*.py'` passed before release
with `1151` tests and `105` skips. Claude and Gemini external reviews accepted
the earlier Goal477 repair; the release sweep is the latest local broad-test
evidence.

## Current Pre-Release Test Gate

Goal 470 adds the current pre-release test/doc/audit evidence:

- local macOS full unittest discovery:
  - `941` tests run
  - `105` expected platform skips
  - `0` failures
  - `0` errors after fixing Goal 429 optional-backend skip behavior
- Linux focused v0.7 pre-release validation on `lestat-lx1`:
  - PostgreSQL 16.13 ready
  - Embree runtime probe: `[4, 3, 0]`
  - OptiX runtime probe: `[9, 0, 0]`
  - Vulkan runtime probe: `[0, 1, 0]`
  - `155` focused v0.7 DB/PostgreSQL/native tests run
  - `0` failures
  - `0` errors

Use [Goal 470 pre-release test/doc/audit report](../../reports/goal470_v0_7_pre_release_test_doc_audit_2026-04-16.md)
for the current gate details.

Use [Goal 477 broad unittest discovery repair](../../reports/goal477_v0_7_broad_unittest_discovery_repair_2026-04-16.md)
for the newer broad local discovery evidence.

Use [Goal 479 release-candidate audit](../../reports/goal479_v0_7_release_candidate_audit_after_goal478_2026-04-16.md)
for the current release-candidate evidence audit after Goal478. It validates
Goal477/Goal478 Codex/Claude/Gemini evidence, invalid Gemini Flash quarantine,
hold/no-release boundaries, and current Goal470/473/475 audit JSON validity.
It does not authorize staging, tagging, merging, or release.

Use [Goal 482 dry-run staging plan](../../reports/goal482_v0_7_post_goal481_dry_run_staging_plan_2026-04-16.md)
for the current post-Goal481 staging-plan evidence. It includes `427`
release-package paths, excludes only `rtdsl_current.tar.gz`, leaves `0`
manual-review paths, and emits `11` grouped advisory `git add -- ...` command
groups. Claude and Gemini accepted the plan, but no staging command was run and
the plan does not authorize staging, tagging, merging, or release.

Use [Goal 483 release-report refresh](../../reports/goal483_v0_7_release_reports_refresh_after_goal482_2026-04-16.md)
for the release-facing documentation refresh after Goal482. It preserves the
same support matrix and hold boundaries, records Claude and Gemini acceptance,
and does not authorize staging, tagging, merging, or release.

Use [Goal 486 post-disk-cleanup artifact-integrity audit](../../reports/goal486_v0_7_post_disk_cleanup_artifact_integrity_audit_2026-04-16.md)
for the artifact-integrity and disk-safety audit after the home-directory Git
cleanup. It has Claude and Gemini acceptance and does not authorize staging,
tagging, merging, or release.

Use [Goal 487 release-hold stability audit](../../reports/goal487_v0_7_post_goal486_release_hold_stability_audit_2026-04-16.md)
for the current release-hold stability evidence. It verifies Goal486
acceptance, disabled home Git metadata, no runaway home-level Git process,
disk safety, and clean `git diff --check`. It has Claude and Gemini acceptance
and does not authorize staging, tagging, merging, or release.

Use [Goal 488 front/tutorial/example/doc consistency audit](../../reports/goal488_v0_7_front_tutorial_example_doc_consistency_audit_2026-04-16.md)
for the current public-doc consistency evidence. It verifies front page,
tutorial, example, and v0.7 release-report alignment and has Claude and Gemini
acceptance.

Use [Goal 489 history synchronization adoption](../../reports/goal489_v0_7_history_synchronization_adoption_2026-04-16.md)
for the current history synchronization evidence. It preserves the external
Antigravity report, archives historical goal docs through Goal431, preserves
current v0.7 root goal docs from Goal432 onward, and updates the root
`history/` dashboard through the current v0.7 hold state.

Use [Goal 490 post-Goal489 pre-stage ledger refresh](../../reports/goal490_v0_7_post_goal489_pre_stage_ledger_refresh_2026-04-16.md)
for the current advisory staging-package ledger. It classifies the dirty tree
after public-doc and history synchronization work, excludes only
`rtdsl_current.tar.gz` by default, and does not authorize staging, tagging,
merging, or release.

## Public Example Surface

Current public DB examples expose:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`

PostgreSQL is not a public example backend flag.
