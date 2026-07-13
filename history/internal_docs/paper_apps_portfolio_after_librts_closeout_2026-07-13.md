# Paper-App Portfolio After LibRTS Closeout

Date: 2026-07-13

## Portfolio Status

The five current paper-app lines are closed at explicit bounded scopes. No
paper app claims complete reproduction of every original dataset, figure,
algorithmic implementation detail, and performance result.

| App | Approved completed scope | System pressure/result | Still unclaimed |
| --- | --- | --- | --- |
| RayJoin | Available-pair Sections 5.2/5.3 and bounded 5.7; v2.14.4 prepared-binary route | Device-columnar prepared pipelines, ordering, and writer-free binary operators | Broad all-input or whole-app semantic/performance parity |
| RT-BarnesHut | Bounded prepared-state same-input force output | Generic aggregate hierarchy, opening policies, frontier/reduce reference and Numba parity | Independent tree construction and full-paper performance |
| RT-DBSCAN | Bounded AuthorOfficial and representative partition gates | Fixed-radius count-threshold primitives and partition-equivalence review discipline | Exact paper preprocessing and arbitrary/full DBSCAN acceleration |
| X-HD | Same-input directed HDResult across seven primary cases | Generic nearest/witness/max-nearest and cell-MBR/frontier capabilities | Exact paper bytes, all figures, author RT-core equivalence, performance parity |
| LibRTS | Scoped correctness and system extraction, externally approved | Generic prepared/mutable AABB columns/indexes, sparse refit, rollback/fail-closed mutation, operation-scoped validity, and batch reuse | Full paper/Figure reproduction, complete range-intersects matrix, author algorithm/performance parity, zero-copy, Embree |

## LibRTS Final Evidence

```text
point_contains exact count matrix = 14/14
range_contains exact count matrix = 14/14
representative PIP relation rows  = 71,626 equal
bounded mutation counts           = [2,1,0,1,0]
range_intersects ledger           = 14 matched / 2 author capacity / 26 not checkpointed
external verdict                  = approve
```

The range-intersects remainder is intentionally frozen under the project
stop-loss rule. More app-only enumeration would produce no new reusable RTDL
capability and answer no unresolved semantic question.

## System Ownership Rule

```text
RTDL core owns generic spatial/dataflow capabilities.
Paper apps own paper inputs, author wrappers, comparators, tolerances,
formatting, workload policy, and claim boundaries.
```

LibRTS preserved this rule. Archive/WKT/cache/comparator work stayed in the
paper app, while the reusable column, prepared-index, mutation/refit, rollback,
and predicate-validity contracts entered the general system surface.

## Repository State Required Before The Next App

The LibRTS source, tests, compact evidence, reports, final external review,
portfolio snapshot, and durable memory must be committed as one intentional
closeout snapshot. No new paper app should be opened on top of an uncommitted
LibRTS worktree.

## Post-Review Verification

The current Goal5453-Goal5525 test range was rerun after the external review,
portfolio, manifest, and documentation updates:

```text
208 tests OK
5 skipped (local OptiX runtime unavailable)
git diff --check: passed
```

The original Goal5525 packet remains the immutable pre-review record of its
176-test internal-closeout run. The 208-test result is a later, broader release
snapshot and does not rewrite that historical evidence.
