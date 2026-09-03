# Goal5842 V6 pre-execution internal hostile review

## Scope and independence

This is an internal hostile review performed before V6 worker zero and before
any V6 timing observation. External review is unavailable while traveling and
is explicitly deferred. This document is not external consensus.

Reviewed surfaces are the V6 preregistration generator and contract, both
identity witnesses, both controllers and worker families, the independent
recount, the two repaired public prepared owners, their native two-phase cache
ABI, the frozen Goal5838 core identities, and the terminal Replication 05
archive. The review asks whether V6 is a scientifically defensible independent
replication, not whether its eventual numbers are favorable.

## Hostile questions and findings

### 1. Is V6 post-result performance tuning?

No accepted Goal5842 result exists. Replication 05 crossed worker zero and is
therefore terminal, but its baseline transaction failed before a controller
result, independent recount, or complete marker existed. Its partial causal
and baseline rows remain archived diagnostics and are prohibited from every V6
estimator. The repair changes no workload, schedule, statistic, success
threshold, task contract, causal arm, or baseline arm. It repairs a generic
public-owner correctness defect: Python requested native cache reuse without
first completing the native two-phase commit. V6 repeats the entire experiment
in a new create-only transaction. Calling V6 a retry or pooling V4/V5 rows is
forbidden.

### 2. Can Python claim reuse while native state names another generation?

Not after the repair. Relation and triangle owners now hash the exact packed
dynamic geometry consumed by the native ABI, commit that digest only after
output and traversal-audit acceptance, read it back, and publish Python cache
identity only after exact equality. Reuse requires both immutable local input
identity and the matching native digest. A native digest mismatch forces a
fresh build. Every `BaseException` window clears the Python identity, including
an interrupt after native commit but before Python publication.

Fault-injection tests cover first commit, successful reuse, native digest
mismatch, traversal-audit rejection, and asynchronous interruption after
commit for both prepared families. The frozen semantic core is byte-identical;
the repair is confined to app-neutral runtime owners and introduces no task or
application vocabulary.

### 3. Does the pre-worker-zero witness actually exercise the failed shape?

Yes. Each RTDL relation and triangle CHECK_ON/CHECK_OFF prepared owner executes
72 complete calls on the same owner, matching the formal steady worker's 8 plus
64 execution shape. Every call validates its output and observed OptiX
classification; triangle validation includes the complete per-ray vector and
weighted reduction. Lifecycle receipts must report exactly 72 executions.
Sphere executes once per arm because it is outside the provider-baseline
steady comparison. The PyOptiX package front door independently executes 72
calls for each of relation and triangle and validates every output.

The phrase "no timing" has a deliberately narrow, machine-checkable meaning:
the witness modules import and call no clock and serialize no duration field or
registered timing observation. Public runtime construction may internally
compute its ordinary `prepare_seconds` field; the witness neither reads nor
records it. Therefore this is a no-registered-timing gate, not a claim that no
transitive callee can consult a clock.

### 4. Does the stronger witness contaminate the performance result?

It intentionally exercises and warms the GPU before worker zero, so it cannot
support a cold-device claim. The registered design does not make that claim.
Formal causal observations use fresh CPU-only processes and measure admission,
not GPU execution. Provider baselines use fresh subworkers, independent first
and steady processes, 18 balanced six-permutation blocks, and eight warm-ups
before 64 steady samples. All hardware generations must run the same witness
and schedule. Residual temperature, clock, and order effects remain possible;
balanced scheduling and per-generation reporting reduce but do not eliminate
them. Raw timing ratios across machines are forbidden.

### 5. Is excluding a repeated Direct witness unfair?

It is a limitation, not a hidden substitution. The Direct executable lacks an
unregistered no-timing witness mode. Replication 05 completed Direct relation
first and steady subworkers, while V6 still reruns every registered Direct row
from scratch after worker zero. The exclusion prevents consuming registered
Direct measurements before the transaction begins; it does not waive Direct
correctness, output, binary-identity, source, or phase checks in the formal
workers. The final report must disclose this asymmetry.

### 6. Are the three tasks enough for a broad language-performance claim?

No. They are three honest matched topology/reducer cases for causal admission
cost; only relation and triangle have all three provider baselines. Sphere has
no Direct/PyOptiX performance denominator. There is no success threshold and
no authorization to generalize two provider-baseline tasks to all RT, to call
the unchecked arm a public optimization, or to explain the whole setup gap by
admission alone.

### 7. Can one Ada result close Goal5842 or support CGO claims?

No. The available RTX 2000 Ada device can supply only the first preregistered
architecture generation. A second complete replay on a distinct NVIDIA
architecture generation and GPU UUID is mandatory. External review remains a
later gate. One-generation evidence may be reported only as an internal first-
generation result with an exact replay plan and fail-closed cross-generation
authority.

## Regression evidence and known debt

- Goal5842 contract and cache tests pass locally.
- Prepared lifecycle, public lifecycle/examples/imports, immutable reuse,
  RTDLEXE, and overflow-focused regressions pass locally.
- Goal5838 frozen-core tests pass, and all three frozen file hashes remain
  unchanged.
- Two Goal5840 historical repair-builder tests fail only because those builders
  regenerate their old scientific-input documents from the current source
  tree; the same 65-test suite passes 65/65 in an independent clean checkout of
  the pre-repair Goal5842 HEAD. The sealed Goal5840 authority remains
  independently verifiable. This current-tree-sensitive historical test debt
  is disclosed rather than rewritten inside Goal5842.
- Broader Goal5773, Goal5796, Goal5798, Goal5801, and Goal5803 discovery runs
  are not green because the current Git tree lacks several historical app,
  JSON, wheel, and evidence-capsule inputs; old import-path and source-string
  assumptions add further failures. None of those missing paths is introduced
  or removed by V6. These broad historical suites are excluded from the
  focused regression denominator and are not represented as passing.

## Verdict

`READY_FOR_NEW_COMMIT_BOUND_REPLICATION06_ON_ONE_FIRST_GENERATION_GPU`

Severity count after the fixes above: P0 = 0, P1 = 0, P2 = 4 disclosed
limitations, P3 = 2 documentation/test-maintenance debts. This verdict permits
only a fresh V6 transaction. It does not authorize a favorable-result claim,
one-generation completion, public speedup wording, external consensus, or a
CGO-ready empirical conclusion.
