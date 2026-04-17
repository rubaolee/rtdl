# RTDL v0.7.0 Release Statement

Date: 2026-04-16
Status: released bounded DB line

## Statement

RTDL `v0.7.0` is the bounded DB-style analytical workload release on the
`codex/v0_7_rt_db` branch.

It adds the first bounded RTDL database-kernel family:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

This package is the canonical release report set for the current `v0.7.0` DB
line.

## What The v0.7 Line Stands On

The bounded `v0.7` line now has:

- DB kernel surface design
- RT DB execution interpretation and lowering contract
- Python truth paths for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- native CPU/oracle execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Embree execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- OptiX execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Vulkan execution for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- PostgreSQL-backed correctness anchoring on Linux
- cross-engine correctness closure on Linux across:
  - Python truth
  - native/oracle CPU
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- bounded Linux performance evidence with PostgreSQL included
- native prepared DB dataset support for:
  - Embree scene reuse
  - OptiX GAS/traversable reuse
  - Vulkan BLAS/TLAS reuse
- columnar prepared DB dataset transfer for:
  - Embree
  - OptiX
  - Vulkan
- refreshed repeated-query performance evidence against PostgreSQL on Linux,
  now rebased against the best PostgreSQL modes tested so far
- Linux fresh-checkout validation after the app-demo and kernel-demo additions:
  - fresh synced checkout imports `rtdsl`
  - missing OptiX and Vulkan runtime libraries build successfully from source
  - Embree, OptiX, and Vulkan runtime probes pass
  - PostgreSQL 16.13 and `psycopg2` are available
  - focused DB correctness tests and prepared-dataset tests pass
  - app-level and kernel-form v0.7 DB demos run under `--backend auto`
- external tester report response after Goal 467:
  - macOS user-perspective correctness report recorded 179/179 PASS across the
    public workload surface on available backends
  - older Windows v0.6 snapshot blocker was fixed in the current branch by
    rejecting stale/incomplete Embree DLLs, adding an explicit
    `make build-embree` probe, and locking graph public API exports
  - fresh Windows current-branch sync verified `rt.csr_graph`, built/probed
    `build/librtdl_embree.dll`, confirmed 22/22 required Embree exports, and
    ran graph Embree examples
- external DB attack-report response after Goal 469:
  - the independent v0.7 DB attack suite was preserved in the repo and rerun
    locally
  - local non-platform gaps were closed for empty DB inputs, float `between`,
    alternate integer `grouped_sum` fields, large boundary row counts, and
    repeated kernel compilation cleanup
  - Linux-only PostgreSQL and native backend gaps were mapped to existing
    Linux gates instead of being silently waived
- pre-release Goal 470 test/doc/audit evidence:
  - full local unittest discovery passes after the Goal 429 optional-backend
    skip fix
  - Linux focused pre-release validation passes with PostgreSQL, Embree, OptiX,
    and Vulkan available from the synced checkout
  - release-facing docs are refreshed through the current Goal 470 hold state
- Goal 471 external v0.6.1 Expert Attack Suite intake:
  - the newer Windows Embree v0.6.1 graph/geometry stress report is preserved
    as supporting external evidence
  - the report's "Certified for deployment" wording is external tester
    language only and is not v0.7 release authorization
- Goal 477 local broad unittest discovery repair:
  - the broader project discovery pattern that includes `goal*_test.py` passed
    before release with `1151` tests and `105` skips
  - the five issues found by that broad sweep were narrow test-harness or
    local-environment failures, not runtime algorithm regressions
  - Goal 477 has Claude and Gemini external-review acceptance and is not release
    authorization
- Goal 479 release-candidate audit after Goal478:
  - verifies Goal477 and Goal478 Codex/Claude/Gemini ACCEPT evidence
  - verifies invalid Gemini Flash placeholder attempts are quarantined
  - verifies current release reports preserve hold/no-release boundaries
  - verifies no active retired non-release metrics task references remain in
    the release path
  - Goal 479 has Claude and Gemini external-review acceptance and is not release
    authorization
- Goal 482 post-Goal481 dry-run staging plan:
  - enumerates `428` current dirty-worktree entries
  - includes `427` release-package paths and excludes only
    `rtdsl_current.tar.gz`
  - leaves `0` manual-review paths
  - emits `11` grouped advisory `git add -- ...` command groups
  - records `staging_performed: false` and `release_authorization: false`
  - Goal 482 has Claude and Gemini external-review acceptance and is not
    staging or release authorization
- Goal 483 release-report refresh after Goal482:
  - updates the audit report, branch statement, support matrix, and
    tag-preparation report with Goal482 evidence
  - preserves hold/no-release/no-tag/no-merge boundaries
  - Goal 483 has Claude and Gemini external-review acceptance and is not
    staging or release authorization
- Goal 486 post-disk-cleanup artifact-integrity audit:
  - confirms report JSON/text artifacts remain intact after the disk-full event
  - records the approved fix for the accidental home-directory Git repository
  - preserves no-stage/no-release boundaries
  - Goal 486 has Claude and Gemini external-review acceptance
- Goal 487 release-hold stability audit:
  - verifies Goal486 acceptance evidence, disabled home Git metadata, no
    runaway home-level Git process, disk safety, and clean `git diff --check`
  - preserves no-stage/no-release boundaries
  - Goal 487 has Claude and Gemini external-review acceptance
- Goal 488 front/tutorial/example/doc consistency audit:
  - refreshes the public front page, tutorials, examples, and release reports
    after Goal487
  - verifies public example commands point to existing files
  - Goal 488 has Claude and Gemini external-review acceptance
- Goal 489 history synchronization adoption:
  - preserves the external Antigravity synchronization report
  - archives historical goal docs through Goal431 while preserving current
    v0.7 root goal docs from Goal432 onward
  - registers root `history/` catch-up rounds through the current v0.7 hold
    state
  - Goal 489 has Claude and Gemini external-review acceptance
- Goal 490 post-Goal489 pre-stage ledger refresh:
  - classifies the current dirty tree after public-doc and history work
  - excludes only `rtdsl_current.tar.gz` by default
  - emits grouped advisory `git add -- ...` command strings
  - records no staging, commit, tag, push, merge, or release action
- Goal 491 post-Goal490 release-hold audit:
  - verifies Goal490 artifacts and Codex/Claude/Gemini acceptance
  - verifies Goal488, Goal489, and Goal490 generated audits remain valid
  - verifies no files were staged during the hold
- Goal 492 ready-for-explicit-staging-authorization hold:
  - verifies Goal491 acceptance and current Goal490 ledger validity
  - confirms the package was ready for explicit release authorization

## What The v0.7 Line Adds

`v0.7` adds:

- the first bounded DB-style analytical kernel family in RTDL
- an RT DB execution model aligned with the accepted RT lowering contract
- a backend story across:
  - CPU/oracle
  - Embree
  - OptiX
  - Vulkan
- PostgreSQL as the external correctness and performance baseline on Linux
- native prepared RT dataset handles for repeated-query workloads
- native columnar table ingestion for the prepared RT dataset path on Embree,
  OptiX, and Vulkan
- Goal 452 as the canonical performance wording:
  - query-only results against best-tested PostgreSQL are mixed
  - setup-plus-10-query total time favors RTDL in the measured Linux evidence
- Goal 464 as the canonical fresh-checkout validation:
  - the current branch package was synced to Linux, brought up from source,
    and validated with PostgreSQL included
  - the Linux GPU used for that run is a GTX 1070, so the run validates backend
    functionality and bounded performance, not RT-core hardware acceleration
- Goal 467 as the canonical response to the newer external correctness and
  Windows audit reports:
  - macOS user-correctness evidence is positive
  - the older Windows stale-DLL/API blocker is fixed and retested from a fresh
    current-branch sync
  - Windows remains a bounded local/runtime surface, not the primary v0.7
    PostgreSQL/GPU performance-validation platform
- Goal 469 as the canonical response to the external v0.7 DB attack report:
  - the attack report and its 105-test suite are preserved
  - local DB edge gaps are closed and regression-tested
  - the first-wave `grouped_sum` RT backend boundary remains integer-compatible
- Goal 470 as the current pre-release test/doc/audit checkpoint:
  - macOS full unittest discovery and Linux focused backend/PostgreSQL testing
    are recorded
  - docs and audit reports are refreshed through the current branch state
  - this is still a hold checkpoint, not release authorization
  - RTDL is not a DBMS and this checkpoint does not change that boundary
- Goal 471 as the current external v0.6.1 Windows attack-suite intake:
  - the Windows Embree graph/geometry stress evidence is positive
  - the report is not a v0.7 DB/PostgreSQL release gate
- Goal 477 as the current newer local broad unittest discovery repair:
  - broad local discovery passed before release with `1151` tests and `105`
    skips
  - this evidence has Claude and Gemini external-review acceptance
- Goal 479 as the current release-candidate audit after Goal478:
  - audit JSON is `valid: true`
  - missing required files: `0`
  - stale retired-metrics references: `0`
  - this evidence has Claude and Gemini external-review acceptance
- Goal 482 as the current dry-run staging command plan:
  - plan JSON is `valid: true`
  - included release-package paths: `427`
  - excluded archive paths: `1`
  - manual-review paths: `0`
  - this evidence has Claude and Gemini external-review acceptance
- Goal 483 as the earlier release-report refresh after Goal482:
  - release-facing reports include Goal482 evidence
  - hold/no-release/no-tag/no-merge boundaries remain explicit
  - this evidence has Claude and Gemini external-review acceptance
- Goal 486 as the post-disk-cleanup artifact-integrity audit:
  - artifact integrity and disk safety are rechecked after the home Git fix
  - this evidence has Claude and Gemini external-review acceptance
- Goal 487 as the current release-hold stability audit:
  - the branch remains stable after Goal486 and still has no stage/tag/merge/release action
  - this evidence has Claude and Gemini external-review acceptance
- Goal 488 as the current public-doc consistency audit:
  - front page, tutorials, examples, and release reports are refreshed through
    the current hold state
  - this evidence has Claude and Gemini external-review acceptance
- Goal 489 as the current history synchronization audit:
  - docs/history and root history chronology are synchronized through the
    current hold state
  - this evidence has Claude and Gemini external-review acceptance
- Goal 490 as the current pre-stage ledger refresh:
  - the current dirty-tree package is mechanically classified after Goal489
  - `rtdsl_current.tar.gz` is the only default exclusion
  - generated staging commands remain advisory only

## What The v0.7 Line Does Not Claim

The `v0.7` line does not claim:

- that RTDL is a DBMS
- that RTDL executes arbitrary SQL
- that the first bounded DB kernels cover arbitrary joins, transactions, or
  multi-group-key grouped queries
- that RTDL replaces warm, already-prepared PostgreSQL in general database
  deployments
- that RTDL beats fully tuned PostgreSQL in general
- that RTDL provides PostgreSQL-level durability, concurrency, indexing,
  optimizer behavior, transactions, or arbitrary SQL
- that the current branch line has already replaced the repository's last tagged
  mainline release

## Relationship To Earlier Releases

Read the repo now as:

- `v0.2.0`: stable workload/package core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and bounded multi-backend expansion
- `v0.6.1`: released corrected RT graph line
- `v0.7`: active bounded DB branch line

## Current Honest Boundary

- RTDL can express and execute a first bounded DB-style analytical workload
  family through the RT kernel path
- correctness is closed across Python, native/oracle CPU, Embree, OptiX,
  Vulkan, and PostgreSQL on Linux
- Embree, OptiX, and Vulkan have native prepared DB dataset paths that reuse
  backend acceleration structures across repeated queries
- Embree, OptiX, and Vulkan have native columnar prepared DB dataset transfer
  paths for the bounded table-ingestion path
- the Linux 200k-row Goal 452 comparison shows all three RT backends winning
  setup-plus-10-query total time against the best PostgreSQL modes tested so
  far, while query-only results are mixed
- Goal 464 confirms that the current package still runs from a fresh Linux
  checkout after building missing OptiX/Vulkan backend libraries
- Goal 464's Linux machine uses a GTX 1070 with no RT cores; do not read that
  run as an RT-core hardware-speedup result
- Goal 467 confirms that the current package addresses the external Windows
  stale Embree DLL/API blocker for the bounded graph/API/Embree deployment
  surface tested on `lestat-win`
- Goal 469 confirms that the imported v0.7 DB attack suite passes and that the
  actionable local edge gaps are closed
- Goal 470 confirms a clean full local unittest discovery and a Linux focused
  pre-release test pass after syncing the current worktree to
  `/home/lestat/work/rtdl_goal470_pre_release`
- Goal 471 confirms the newer external Windows v0.6.1 Expert Attack Suite
  report has been preserved and bounded as supporting graph/geometry evidence,
  not v0.7 DB release authorization
- Goal 477 confirms locally that the broader `*test*.py` unittest discovery
  pattern passes after narrow test-harness repairs and has Claude and Gemini
  external-review acceptance
- Goal 479 confirms the current release-candidate evidence package remains
  mechanically valid after Goal478 and has Claude and Gemini external-review
  acceptance
- Goal 482 confirms the current dry-run staging command plan is mechanically
  valid after Goal481 and has Claude and Gemini external-review acceptance
- Goal 483 confirms the release-facing reports are refreshed after Goal482 and
  has Claude and Gemini external-review acceptance
- Goal 486 confirms artifact integrity after the disk-full/home-Git incident
  and has Claude and Gemini external-review acceptance
- Goal 487 confirms the current release-hold state remains stable after Goal486
  and has Claude and Gemini external-review acceptance
- Goal 488 confirms the public front page/tutorial/example/release-doc surface
  is current and has Claude and Gemini external-review acceptance
- Goal 489 confirms the history system is synchronized through the current hold
  state and has Claude and Gemini external-review acceptance
- Goal 490 confirms the post-Goal489 dirty tree has a current advisory
  pre-stage ledger, with no staging or release action performed
- Linux carries the main correctness/performance validation story for this line
- this release remains bounded by the v0.7 support matrix and evidence reports
