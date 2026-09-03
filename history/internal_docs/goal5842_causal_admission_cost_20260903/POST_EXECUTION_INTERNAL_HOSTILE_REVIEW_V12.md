# Goal5842 V12 post-execution internal hostile review

Date: 2026-09-03

Review mode: internal hostile self-review only. External review and consensus
are owner-deferred while traveling.

## Question

Does the completed Ada transaction support a causal statement about generic
admission cost, a fair current-implementation baseline, and Goal5842 closure?

## Evidence reviewed

- exact V12 preregistration and all 73 frozen source-manifest rows;
- complete 3,790,441-byte V12 archive;
- all seven stage commands, return codes, stdout, and stderr;
- 216 causal receipts and controller result;
- 216 baseline subworker receipts, 108 composites, and controller result;
- three timer-free identity witnesses;
- original independent recount and a byte-identical local replay;
- generated first-generation authority and its fail-closed mutation test;
- V11 terminal failure report and complete V11 archive.

## P0 findings

None found within the one-generation evidence boundary.

## P1 findings

1. Goal5842 is not complete. Only Ada is represented; the preregistered minimum
   is two distinct GPU architecture generations.
2. V12 is not result-blind. V11 exposed the same registered timings before V12
   corrected the independent validator's arm-specific receipt schema. V11 is
   preserved as terminal, its rows are excluded, and V12 must be described as
   a disclosed post-result full replay rather than a blind replication.
3. The provider baseline is adverse. RTDL setup is 10.47x--16.08x the matched
   alternatives; RTDL relation steady execution is 3.00x PyOptiX and 10.06x
   Direct; RTDL triangle steady execution is 108.75x PyOptiX and 188.95x
   Direct. These rows cannot be hidden behind the favorable causal diagnosis.
4. The triangle public outputs are exact, but hidden work is not identical.
   RTDL materializes an internal per-ray vector and performs host reduction;
   Direct and PyOptiX copy only the public scalar in the registered interval.
   This is a fair comparison of current implementations under the same public
   contract, not proof of intrinsic RTDL language overhead.

## P2 findings

1. The causal experiment isolates admission construction only. It does not
   isolate every checker invocation during later target materialization, prove
   that check removal is safe, or predict end-to-end speed after removal.
2. The 0.78%--0.83% fractions are post-registered diagnostics formed from
   separately estimated medians. They are useful for prioritization but are
   not new primary estimands and must not be assigned bootstrap intervals.
3. Phase medians do not algebraically sum to the setup median because each is
   summarized independently. The 95.1%--96.6% materialization-plus-prepare
   fractions are descriptive only.
4. The first-generation verifier requires the exact Git objects for source
   commit `04305fc8...`; the complete evidence archive alone does not embed a
   hermetic source repository or Python environment. This is acceptable for
   current Git-backed review but remains an artifact-packaging limitation.
5. Direct exposes no close-phase timing. The design correctly forbids an
   all-arm close comparison; no synthetic zero may be substituted.
6. The combined Goal5840/Goal5842 regression is `116/118`; the two errors are
   the pre-disclosed Goal5840 current-tree-versus-historical-attempt custody
   comparisons. Goal5842 tests pass, but the repository must not be described
   as having an all-green combined historical suite.

## P3 findings

1. The Ada pod is one shared-cloud environment. Idle-process gating reduces
   obvious interference but does not provide exclusive physical-host proof.
2. The two provider-baseline tasks do not represent arbitrary RT programs, and
   the third causal task has no fabricated provider baseline.
3. No cross-machine raw-time ratio should ever be computed. The second
   generation is a direction/diagnosis replication, not a faster-GPU contest.

## Hostile attacks and responses

### "The checker explains the performance gap"

Rejected on this hardware. The primary admission delta is 27.7--38.0 ms while
the observed RTDL setup disadvantage is about 4.1--4.9 s. Admission is real but
not dominant.

### "Disable the checker to make RTDL competitive"

Rejected. Check-off is a private experiment-only counterfactual. Later
materialization still revalidates identity, and the experiment supplies no
safety case for a public unchecked API.

### "The baseline proves the language is inherently 189x slower"

Rejected. It proves the current measured implementation is that slow on the
triangle steady route under the registered public-output boundary. It also
identifies avoidable internal vector materialization and host reduction. No
intrinsic lower bound follows.

### "V12 cherry-picks after seeing V11"

Partially valid as a risk, but not as a row-pooling allegation. V12 is openly
post-result, repeats the full unchanged schedule, has no success threshold,
retains every adverse row, changes only an independently demonstrable receipt
schema defect, and binds the terminal V11 archive. This reduces but does not
erase the need for a distinct-generation replay.

### "One successful pod run is enough"

Rejected by the preregistration and machine-readable authority. One generation
cannot set the completion, cross-generation, or public-performance flags.

## Engineering consequence

The next performance work should not weaken generic admission. The dominant
targets are:

1. cache and reuse prepared target state instead of reconstructing it per
   worker or route;
2. remove redundant Python-to-native materialization and copies;
3. keep triangle continuation/reduction device-resident and return only the
   public scalar when that is the contract;
4. separate one-time compilation/pipeline construction from reusable prepared
   execution;
5. rerun the same fair baseline after such changes under a new preregistered
   goal, not inside Goal5842.

These are substantial runtime/compiler contributions. Further polishing of the
Goal5842 harness without obtaining the required second architecture would be
low-value activity.

## Verdict

`ACCEPT_AS_COMPLETE_FIRST_GENERATION_EVIDENCE__REJECT_GOAL5842_COMPLETION`

The Ada transaction and authority are technically sound at their stated scope.
The only remaining Goal5842 scientific execution is the exact distinct-GPU-
generation replay and cross-generation gate in
`SECOND_GENERATION_REPLAY_PLAN_V12.md`. External review remains a later gate
and is not claimed.
