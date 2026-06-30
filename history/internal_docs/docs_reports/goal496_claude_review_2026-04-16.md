# Goal 496 External Review — 2026-04-16

Reviewer: Claude Sonnet 4.6 (independent pass)

## Verdict: ACCEPT

---

## Scope

Files reviewed (all working-tree changes against the decision report):

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md` (new file)
- `docs/quick_tutorial.md`
- `docs/tutorials/README.md`
- `docs/tutorials/db_workloads.md`
- `docs/tutorials/graph_workloads.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/features/README.md`
- `examples/README.md`

---

## Criteria Checked

1. User-value-first wording improves usefulness, attractiveness, and comprehensiveness.
2. v0.7 honesty boundaries preserved.
3. No unsupported performance claims introduced.

---

## Findings

### 1. README.md

The new "Why RTDL Is Useful" section is accurate and well-framed. The 10x claim is
explicitly scoped to authoring burden: "an engineering-productivity target, not an
unbounded speedup claim." The Version Status, Current Limits, and Choose Your Path
sections carry all prior honesty boundaries without reduction. The front page is
now navigable for first-time users without removing any audit pointer. No issue.

### 2. docs/README.md

The ten-minute evaluation path and new-user ordering are correct and point to
exact boundaries at step 4 (v0.7 Support Matrix). Historical and maintainer
material is cleanly separated under its own heading. No issue.

### 3. docs/current_architecture.md (new)

The user contract, RTDL-owns/Python-owns split, and backend table are accurate
against the v0.7 release surface. The 10x claim is stated as "intended benefit"
with an immediate qualifier: "This is not a blanket performance claim. Performance
depends on workload, backend, host hardware, data shape, and preparation strategy.
The release reports define the exact current performance evidence." The Current
Boundaries section explicitly disclaims renderer, DBMS, SQL engine, universal
speedup, and cross-platform parity. No issue.

### 4. docs/quick_tutorial.md

The intro paragraph correctly explains the burden-reduction goal before the first
command. The 10x framing ("It is not a promise that every backend is always 10x
faster") is clearly stated. Commands and expected outputs are consistent with the
v0.7 release surface. No issue.

### 5. docs/tutorials/README.md

Tutorial ladder is organized around the one-kernel-shape value proposition.
Three learning tracks (language basics, workload tutorials, application demos)
map to the real released surface. No inflated claims. No issue.

### 6. docs/tutorials/db_workloads.md

The "What Data Becomes What Data" table is accurate. The "Important boundary"
block (not a DBMS, not SQL execution) is preserved. Goal 452 is cited correctly:
"query-only results are mixed against the best PostgreSQL modes tested so far,
while setup-plus-10-query total time favors RTDL in the measured Linux evidence."
Goal 492 referenced for release-readiness hold. No issue.

### 7. docs/tutorials/graph_workloads.md

The "What Data Becomes What Data" table is accurate. Orchestration boundary is
clearly stated: "Python still owns whole-algorithm orchestration such as
multi-level BFS loops or full-graph accumulation." No issue.

### 8. docs/release_facing_examples.md

The "Choose By Job" table is an appropriate navigational addition. Goal 452 and
Goal 492 honesty boundary block matches canonical wording. No issue.

### 9. docs/rtdl_feature_guide.md

"Practical Promise" section correctly frames 10x as developer-productivity, not
automatic speedup ("Use release reports for measured performance claims"). The
"What RTDL Cannot Yet Claim" section is fully preserved. No issue.

### 10. docs/features/README.md

"Choose By Workload Shape" table maps correctly to released feature homes. The
benefit statement ("write the workload contract once, then let RTDL handle
traversal/refinement/backend plumbing inside documented release limits") is
accurate and bounded. No issue.

### 11. examples/README.md

Purpose table is accurate. DB boundary block correctly notes that PostgreSQL is a
correctness/performance anchor, not a public CLI backend flag. No issue.

---

## Honesty Boundary Check

All eleven files:

- Frame "10x reduction" as authoring burden, not runtime speedup.
- Redirect to release reports and support matrices for exact performance claims.
- Preserve RTDL-is-not-a-DBMS, RTDL-is-not-a-renderer, Linux-primary-validation,
  and per-backend-availability disclaimers.
- Do not claim OptiX/Vulkan availability on non-Linux platforms.
- Do not claim arbitrary SQL execution.
- Do not upgrade Goal 452 mixed query-only results to a clean RTDL win.
- Release reports and historical docs are not modified by this change set.

No unsupported performance claim was introduced in any file.

---

## Decision Rule Compliance

The decision report (goal496_public_docs_competing_versions_decision_2026-04-16.md)
selected Version B for all eleven public surfaces reviewed here. Each file
matches the stated Version B intent: user-value-first framing with Version A
precision boundaries preserved nearby or in adjacent release-report pointers.
Historical architecture is retained as historical. Release reports are unchanged.
The new `docs/current_architecture.md` correctly fills the live-architecture gap
identified in the decision report without corrupting preserved history.

---

## ACCEPT
