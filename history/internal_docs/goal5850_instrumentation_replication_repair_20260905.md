# Goal5850 instrumentation replication repair

Date: 2026-09-05 America/New_York

Status: `TWO_FAILURES_RETAINED__V3_REPLICATION_IMPLEMENTED__FRESH_TRANSACTION_PENDING`

## 1. Decision

Goal5850 has two retained transactions that stopped before formal worker zero.
The first exposed a pair-discarding v1 estimator. The second used the corrected
pair-first v2 estimator, but exposed that one cold-process observation per
condition and block cannot resolve a 5% instrumentation limit on this host.

The v3 repair does not change the endpoint, 5% limit, tasks, eight top-level
blocks, ON/OFF treatment, process isolation, formal workload, formal arms,
formal timing count, or any performance threshold. It adds 16 fresh-process
replicates for each task/block/mode cell. Each block first takes the median of
its 16 OFF endpoints and the median of its 16 ON endpoints. The registered
block value is the ratio of those two medians. The gate remains
`max(0, median(eight block ratios) - 1.0) <= 5%`.

This produces 512 nonformal instrumentation workers. The cost is intentional:
the gate must distinguish instrumentation cost from cold CUDA/OptiX startup
variance rather than pass or fail according to eight noisy draws.

## 2. Retained v2 failure

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX 2000 Ada Generation |
| GPU UUID | `GPU-2fe387f0-ed74-e62c-0686-750461318361` |
| Compute capability | `8.9` |
| Source commit | `5f19422160aa1af31b0d28eb7db970e0b435169e` |
| Source tree | `d7a595508c129c0f40a17f8dfa614c90603415c7` |
| Failure seal | `585d014d0d8eb167dfb109ac54fe65cb9153af717725eb4c4bc98a0f45992d55` |
| Failure archive SHA-256 | `e636860a4bb230b5246eaafad22e83bce3e26ef72e2b653be17e73fb778f7e60` |
| Instrumentation workers | 32/32 completed |
| Formal timing cells | 0/80 started |
| Retry/discard | 0/0 |

The archive was copied off the pod and independently rehashed at the same
digest under
`/Users/rl2025/goal5848_evidence/ada89_rtx2000_5f194221_transaction1_20260905/`.
It remains an immutable failure and is ineligible for pooling or relabeling.

The v2 within-block ratios were:

| Task | Eight ON/OFF ratios | Median | Gate |
| --- | --- | ---: | --- |
| Relation | 1.383167, 3.278578, 1.192990, 3.159851, 1.299752, 0.621851, 0.370232, 1.339084 | 1.319418x | Fail |
| Triangle | 1.101593, 4.050686, 0.641592, 2.796249, 4.329143, 0.864883, 1.184014, 0.727627 | 1.142803x | Fail |

The range and sign changes are inconsistent with a stable instrumentation
effect. Individual endpoints ranged from about 0.38 to 2.10 seconds. The ON
partition showed CUDA-primary-context and provider-bind intervals varying by
more than one second across otherwise identical fresh workers.

## 3. Causal diagnostics

All diagnostics in this section are explicitly non-evidence. They do not
repair either failed transaction and cannot enter a formal estimator.

A fixed two-second delay before every worker did not make the single-draw
relation gate pass. Therefore immediate process teardown alone is not the
cause.

An eight-block four-condition diagnostic separated Python timers and native
tracing:

| Task | Python only / OFF | Native only / OFF | Both / OFF |
| --- | ---: | ---: | ---: |
| Relation | 0.937666x | 0.622561x | 1.178286x |
| Triangle | 1.199481x | 1.229490x | 0.814661x |

The contradictory directions rule out a single instrumentation component as
the observed 10--30% cause. The code path contains only a small number of
`perf_counter_ns`, `steady_clock`, and stderr trace operations; the observed
hundreds-of-milliseconds swings are cold-process variance.

A separately fixed-seed, balanced-randomized 32-block diagnostic then retained
32 ON and 32 OFF endpoints per task. Its result file SHA-256 is
`7b53c102fef91d8b9421599e982ad514d0e816aa5a437a20868c04afea013653`.

| Task | Median of 32 paired ratios | Ratio of ON/OFF marginal medians |
| --- | ---: | ---: |
| Relation | 0.846255x | 0.809243x |
| Triangle | 1.008125x | 0.941607x |

The larger fixed schedule finds no positive effect over 5%. It does not become
formal evidence; it establishes that the old 8-pair, one-draw gate was
underpowered and motivates replication.

## 4. V3 frozen protocol

- authority schema:
  `rtdl.goal5848.instrumentation_overhead_authority.v3`;
- eight registered blocks;
- two tasks and two modes;
- 16 fresh-process replicates per task/block/mode;
- 512 total nonformal workers;
- deterministic traversal of replicate, block, task, and mode with direction
  reversals that distribute temporal drift;
- block estimator: ON endpoint median divided by OFF endpoint median;
- final estimator: median of eight block ratios minus one, clamped at zero;
- unchanged limit: 50,000 ppm;
- every replicate retained, with worker/process/stdout/stderr hashes bound into
  the authority; and
- independent reconstruction in both preflight and final transaction
  authority code.

## 5. Bias controls and claim boundary

This is a second post-failure protocol repair and therefore requires stronger
controls, not weaker wording:

- both earlier failures remain named and hash-bound;
- no old endpoint may be reused in v3;
- v3 must be committed and pushed before its first worker;
- v3 must use a new preregistration and output root;
- all 512 workers must be retained; no retry or discard is allowed;
- the 5% threshold is unchanged;
- formal worker count remains exactly 80 after preflight;
- no public or manuscript performance claim is authorized by this repair; and
- external review must examine the post-hoc repair before publication.

Goal5850 remains open until a wholly fresh v3 transaction passes every
preflight and formal gate and produces byte-identical independent authority
recounts.
