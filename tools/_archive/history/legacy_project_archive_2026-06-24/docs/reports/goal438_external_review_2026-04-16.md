# Goal 438 External Review

Date: 2026-04-16

## Scope

Review of the refreshed `v0.7` branch release-gate package after native prepared DB dataset support (Goals 434–436) and the repeated-query performance gate (Goal 437) are complete. Checked: front page, docs index, quick tutorial, DB tutorial, release-facing examples, DB feature home, v0.7 release package files (release statement, support matrix, audit report, tag preparation), Goal 437 evidence, and prior Codex review (Goal 431).

## Findings

**Front page (README.md):** Clean. The v0.7 surface bullet now correctly includes "native prepared DB dataset reuse on Embree, OptiX, and Vulkan." The "Current Release State" blurb covers the Linux 200k-row repeated-query gate. PostgreSQL is framed correctly as an external baseline throughout. No overclaims.

**Docs index (docs/README.md):** Live state summary is consistent with the achieved surface. Both v0.7 branch links (statement and support matrix) are present under the new user path for DB branch work.

**Quick tutorial:** DB tutorial step (step 6) is present; optional DB examples are correctly noted as bounded v0.7 branch work. No overclaims.

**DB tutorial (docs/tutorials/db_workloads.md):** Lists all three `prepare_*_db_dataset` APIs under current correctness anchors. PostgreSQL correctness gate commands are present. "What Is Still Missing" section is honest (multi-group-key, final columnar ingestion, tag decision).

**Release-facing examples:** Public DB example surface now exposes `cpu_python_reference`, `cpu`, `embree`, `optix`, and `vulkan`. References Goal 437 for repeated-query performance evidence. Boundary language is honest (native prepared dataset APIs exist but CLIs intentionally stay small).

**DB feature home (docs/features/db_workloads/README.md):** Prepared dataset APIs documented, Goal 437 evidence linked, current limits stated (no DBMS, no joins, one group key, ctypes ingestion caveat).

**v0.7 release package:**
- Release statement: complete through Goal 437; lists native prepared dataset support and repeated-query performance evidence explicitly.
- Support matrix: performance table present (3.21x–5.25x speedup vs PostgreSQL setup+10-query total across all workload/backend pairs); ctypes ingestion caveat noted; platform boundary is correct.
- Audit report: documents both correction passes; confirms public example surface is now aligned with achieved backend closure.
- Tag preparation: hold decision maintained; hold condition is correctly justified.

**Goal 437 evidence:** All three workload/backend pairs show RTDL setup time below PostgreSQL setup time and RTDL median query time below PostgreSQL median query time (`wins_from_first_query`). Correctness hashes are present and consistent. Claim boundary language is appropriately narrow (bounded in-memory RT over synthetic denormalized rows, not a general DBMS claim).

**Prior Codex review (Goal 431):** ACCEPT. That review covered through Goal 430. The incremental from Goal 431 to Goal 438 — native prepared dataset support and repeated-query gate — is now reflected in all updated documents.

## Blockers

None.

## Decision

ACCEPT

The v0.7 branch release-gate package is internally coherent after the Goal 438 refresh. All documents are consistent with each other and with the Goal 437 performance evidence. Boundary language is honest throughout: the line is branch-packaged and performance-gated, not tagged as the next mainline release, and no document overclaims DBMS capability or general SQL acceleration.
