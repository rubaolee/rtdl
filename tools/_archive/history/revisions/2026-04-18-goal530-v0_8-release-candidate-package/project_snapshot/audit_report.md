# RTDL v0.8 Release-Candidate Audit Report

Date: 2026-04-18
Status: release candidate / not yet tagged

## Audit Scope

This audit checks the bounded `v0.8` app-building release-candidate package for:

- app-suite completeness
- public docs/tutorial/example consistency
- workload-scope honesty
- backend/platform boundary consistency
- performance-claim consistency
- macOS and Linux post-doc-refresh validation
- history-registration completeness through Goal529

## Findings

### App Suite

The accepted v0.8 app suite contains six applications:

- Hausdorff distance
- ANN candidate search
- outlier detection
- DBSCAN clustering
- robot collision screening
- Barnes-Hut force approximation

Each app uses existing RTDL primitives and Python app logic. No new internal
language release surface is claimed.

### Programming Model

Goal517 documents the current app model:

```text
input -> traverse -> refine -> emit
```

The audit finds this framing accurate for v0.8. RTDL owns the candidate/query
kernel. Python owns orchestration, reductions, labels, quality metrics, and
output.

### Workload Scope

Goal519 and Goal521 define the workload-universe and scope decision matrix.

The audit finds the scope honest:

- v0.8 does not claim all workloads from the survey paper are complete.
- completed v0.8 apps are the supportable app-building subset.
- deferred workloads have documented reasons.
- unsupported workloads are not silently represented as complete.

### Documentation Consistency

Goals 525-527 refreshed public docs after the Stage-1 proximity performance
evidence:

- front page and docs index now describe current v0.8 status
- release-facing examples list all six apps
- examples index carries the Goal524 boundary for ANN/outlier/DBSCAN
- capability-boundary docs distinguish bounded ANN candidate reranking from
  full ANN/vector-index systems
- stale wording such as "the other two v0.8 apps" and "do not yet have Linux
  performance closure" was removed from public docs

### Validation

Goal528 macOS local audit:

- full test discovery: `232` tests, `OK`
- public command harness: `62` passed, `0` failed, `26` skipped

Goal529 Linux validation:

- full test discovery: `232` tests, `OK`
- public command harness: `88` passed, `0` failed, `0` skipped
- Embree, OptiX, and Vulkan runtime probes pass from a fresh synced checkout

### Performance Claims

The audit finds current performance wording bounded:

- Hausdorff evidence is Goal507-specific.
- Robot/Barnes-Hut evidence is Goal509-specific.
- Stage-1 proximity evidence is Goal524-specific.
- Goal524 does not claim external-baseline speedups because SciPy was absent in
  that Linux validation checkout.
- No v0.8 doc claims RTDL beats SciPy, scikit-learn, FAISS, HNSW/IVF/PQ
  systems, production clustering systems, or production anomaly-detection
  systems.

### History

The complete-history map is valid through Goal529:

- structured revision rounds: `104`
- tracked files: `5319`
- history dashboard includes Goals 525-529
- Codex, Claude, and Gemini consensus records exist for Goals 525-529

## Remaining Honest Boundary

The release candidate remains bounded:

- current released version remains `v0.7.0` until explicit tag authorization
- v0.8 is app-building work, not a full language redesign
- v0.8 does not claim a new DBMS, ANN system, robotics stack, clustering
  engine, simulation framework, or renderer
- Linux is the primary validation platform
- macOS is a bounded local platform
- Windows evidence is preserved from earlier lines but is not the primary
  v0.8 post-doc-refresh gate

## Audit Verdict

The v0.8 release-candidate documentation package is coherent and bounded.

Status: **ACCEPT PENDING EXTERNAL REVIEW**.
