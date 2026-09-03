# Goal5842 causal admission-cost and fair-baseline design

## Scientific purpose

Goal5798 observed 162--223 ms more post-import setup time for RTDL than the
matched PyOptiX-compatible arm, but its RTDL worker combined protocol
validation and code generation and its arm paths did not consume identical
generated artifacts.  Those data therefore cannot identify admission as the
cause.  Goal5842 addresses that causal gap rather than adding another
application or tuning an execution kernel.

The primary estimand is an absolute within-block latency difference between a
cold, normal public generic-family admission and a cold, experiment-only
unchecked construction.  Both arms start in fresh processes, call the same
route factory for the first time, call the same provider projection, and
construct the same capability type.  The unchecked arm skips only the generic
core's plan, artifact, descriptor, provider-coverage, and projection-integrity
checks.  It reaches a private construction token, is not a public API, and is
not safe for user code.

No normal admission runs before the registered interval.  After timing, both
arms run normal public admission solely to compare the plan, artifacts,
provider projection, and provider descriptor digests.  Later target
materialization independently revalidates plan, artifact, descriptor, and
projection identity.  Therefore this experiment identifies the incremental
generic-admission phase only; it neither proves that the checks may be removed
nor predicts that full setup would fall by the same amount.  Generated
executable, PTX, native library, input, and output identities are checked by
the no-timing GPU witness and provider cohort.  Any identity mismatch aborts
the transaction.

The preregistration records exact SHA-256 identities for every task input,
full independent oracle, and cross-arm public output, plus primitive/query
cardinalities and baseline eligibility.  These values are checked against the
live deterministic builders before execution; source pinning is not the only
workload freeze.

## Cohorts

The causal admission cohort contains three public generic-lifecycle routes:

1. custom-AABB bounded relation count;
2. built-in-triangle weighted all-hit reduction;
3. built-in-sphere per-query any-hit count.

The provider comparison cohort remains relation and triangle only.  These are
the two tasks with already matched Direct CUDA/OptiX and PyOptiX-compatible
implementations.  Sphere is not assigned a fabricated Direct, PyOptiX, or OWL
row.  OWL remains responsibility analysis unless an exact public executable
arm is frozen before worker zero.

The common public output contract is the canonical relation-row set for the
relation task and the checked weighted scalar for the triangle task. Direct,
PyOptiX, and the fixed-protocol RTDL owner each validate the triangle per-ray
vector in separate pre-worker-zero, non-timed witnesses. Current RTDL's generic
public adapter exposes only the scalar, so the stronger internal vector is not
fabricated as a cross-arm generic result. Capacity, overlap threshold, ray
bounds, geometry, queries, and weights are all part of each input digest.

## Phase boundaries

Each causal worker reports route declaration and artifact binding separately
from provider projection plus either public admission or unchecked capability
construction.  The second phase is the primary causal estimand.  The sum from
route creation through capability construction is a secondary result, and the
route-only ON-minus-OFF difference is a negative control.  The post-estimand
normal admission is intentionally excluded and explicitly recorded; it cannot
warm either registered arm.

Every provider-baseline worker reports deterministic input materialization,
route declaration and artifact binding, provider projection and generic-family
admission, runtime target/toolchain binding, target materialization, native
prepare, first complete execution, steady complete execution, and close.
The registered execution interval ends when the implementation has materialized
the common public result and completed its required status checks. Experimental
comparison with the frozen oracle occurs immediately afterward and is never
timed. For the triangle task, the explicit Goal5842 Direct and PyOptiX modes do
not copy the auxiliary per-ray vector to host during this interval. RTDL's
current internal per-ray materialization and host reduction remain measured as
real implementation cost.

Every three-arm baseline schedule row is a composite of two independent fresh
processes.  The first process measures input, setup, first complete execution,
and close.  The second performs the same setup, eight untimed complete warmups,
and 64 measured complete executions.  The PyOptiX arm consumes the already
materialized frozen fixture; it may not regenerate a second unmeasured input.
`setup_total` includes declaration/admission where applicable, target
and toolchain binding where applicable, target materialization, and native preparation.  It excludes input construction,
first execution, steady execution, and close.  Direct's inherited C++ worker
does not expose destruction timing, so no cross-arm close ratio is permitted.

## Ordering and statistics

Each of the three tasks uses 18 four-worker blocks.  Blocks alternate ABBA and
BAAB, yielding 36 cold public-admission and 36 cold unchecked-construction
workers per task.  The primary block statistic is the median of two public
admission-phase observations minus the median of two unchecked-construction
phase observations.  The reported primary point estimate is the median of 18
block deltas in absolute nanoseconds.  The full route-to-capability delta is a
secondary statistic.  A fixed-seed 10,000-draw percentile bootstrap reports
indices 249 and 9749 for each.  Ratios against the unchecked arm are forbidden.

Steady execution uses eight warmups and 64 complete execution samples per
worker, each followed immediately by mandatory out-of-interval oracle
validation. Baseline ordering uses all six permutations of Direct,
PyOptiX-compatible, and checked RTDL across 18 blocks per task.  Adverse rows
are retained.  No success threshold is selected.

## Hardware and failure boundary

The exact same frozen harness must run on at least two distinct NVIDIA GPU
architecture generations.  Results are reported per hardware target; raw
times are not divided across machines.  The available Ada pod can satisfy at
most one generation.  No driver, CUDA, or OptiX version floor is imposed:
environment negotiation is engineering work performed before worker zero.

After worker zero, there is no retry, row replacement, failed-row deletion,
task change, timing-boundary change, or RTDL-only optimization.  Incorrect
workers are disclosed and excluded from aggregates.  Any byte-identity breach
aborts the formal transaction.

Before worker zero, one execution authority binds the clean Git commit,
preregistration, Python executable, native DSO and build manifest, Direct
binary, CUDA device source, OptiX/CUDA headers, PyOptiX package/version/source
identity, CuPy identity, GPU UUID, driver, and architecture generation.  A
non-timed GPU witness must show checker-on/off executable and output identity
for all three tasks. Additional non-timed witnesses must establish the full
triangle per-ray oracle for RTDL, PyOptiX, and Direct before worker zero. After
both controllers finish, a separately implemented
recount reads every raw receipt and independently recomputes all medians,
within-block deltas, ratios, and fixed-seed bootstrap intervals.

The first hardware transaction is explicitly insufficient for Goal5842's
cross-generation gate.  A second NVIDIA GPU from a distinct architecture
generation must execute the same committed bytes, schedules, workloads, and
recount procedure.  The final gate rejects duplicate generations, duplicate
GPU UUIDs, commit drift, or preregistration drift.  It preserves each machine's
absolute results separately and never computes a cross-machine raw-time ratio.

## Claim ceiling

V9 is an append-only fair-baseline redesign after V8 failed before worker zero.
Prior V4/V5 partial timing is disclosed and not pooled. The V9 correction was
motivated by source-level output/timing-contract inspection, but it is not
called a strict replication because earlier partial timing existed.

V10 supersedes the locally frozen V9 before any V9 formal execution. It only
restores an inherited PyOptiX source-level bulk-copy contract without changing
runtime semantics, tasks, estimands, schedules, witnesses, timing boundaries,
or statistics. Six unregistered correctness-preflight calls comprising eight
OptiX launches are disclosed separately and are excluded from all estimators.

Goal5842 may attribute only the measured incremental generic-admission delta.
It may not claim that this delta explains all prior setup overhead, that the
unchecked arm is a supported optimization, that two provider tasks represent
arbitrary RT programs, or that two GPUs establish hardware-independent
performance.  External review and consensus remain deferred while the owner
is traveling.
