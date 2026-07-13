# Goal4906 — Cold/Hot Branch Reconciliation After Goal4896

Date: 2026-07-03

## Verdict Requested

`completed_goal4888_goal4896_reconciliation__prepared_hot_branch_a_selected`

## Why This Goal Exists

Claude's Goal4896 review approved the LSI pair-id rows optimization, but found a
decision-critical contradiction:

- Goal4888 classified the route as `native_rt_traversal_dominated`.
- Goal4896 and the later Goal4901-Goal4905 evidence show that, in the prepared
  hot/replay state, the dominant costs are no longer raw point-location traversal.

This goal reconciles those two facts before any further implementation proceeds.
The purpose is to prevent a wrong branch decision from sending the next work back
into the V3 failure mode: optimizing a layer before proving that layer is the
bottleneck.

## Short Answer

Goal4888 was not useless, but its branch conclusion was made from a
cold/unprepared or partly unaccounted state. It must not control the
prepared-hot optimization route.

For the prepared-hot target, the current evidence selects:

```text
Branch A: materialization / prepare / replay / app-layer continuation
```

not:

```text
Branch B: native RT traversal dominated
```

Branch B remains a long-term language/runtime research direction if the goal is
to approach the author's fused OptiX kernel. It is not the immediate next
evidence-supported optimization branch for the current prepared-hot route.

## Evidence Reconciliation

| Evidence | State Measured | Key Numbers | Interpretation |
|---|---|---:|---|
| Goal4888 | Earlier hot-path ledger from Goal4886, before later prepared/cache accounting | vertex PIP map0 `10.700s`, native traversal `9.784s`; LSI `5.667s` | Correctly warned that Goal4887's `3-8s` target was unjustified. But this state does not represent the later prepared-hot replay target. |
| Goal4896 | Same-wrapper hot-cache LSI comparison | old LSI `5.546s`; new pair-id LSI `2.856s`; end-to-end `16.398s -> 14.055s` | Shows removable materialization/exact-refine work existed. This directly contradicts a pure native-traversal-only diagnosis. |
| Goal4901 | Same-process accounted steady repeat | total `11.320s`; point-location prepare map1 `4.123s`; writer `2.529s`; LSI `1.908s`; vertex PIP map0 `1.117s` | The `~9.8s` mystery became measured prepare/cold/setup cost. In steady accounted state, PIP traversal is not the dominant hot body item. |
| Goal4902 | Reused prepared point-location sessions | hot body `11.320s -> 6.915s`; writer `3.031s`; LSI `1.819s`; vertex PIP map0 `1.086s` | Reusing existing public prepared PIP sessions gives a real hot-body win. Setup remains real, but hot route is Branch A. |
| Goal4904 | Prepared LSI + prepared PIP replay | hot body `6.450s -> 4.638s`; LSI `1.814s -> 0.006s`; writer `2.562s`; vertex PIP map0 `1.096s` | In prepared replay, LSI traversal/materialization is essentially removed. Writer/chain construction becomes the largest hot cost. |
| Goal4905 | Writer internal breakdown | writer `2.674s`; file write `0.044s`; chain loop map0 `1.955s`; chain loop map1 `0.532s` | File I/O is not the bottleneck. Python chain construction/bookkeeping is. |

## What Was Wrong With The Earlier Branch Decision

The earlier error was not "Goal4888 measured nothing." It measured a real
problem and prevented a premature Goal4887 implementation.

The error was treating its early `native_rt_traversal_dominated` label as if it
applied to the later prepared-hot target.

The later evidence shows three distinct states:

1. **Cold/single-run setup state**
   - CDB load/pack, point-location preparation, first-touch/JIT, and session
     setup are real.
   - This state is relevant to one-off command-line reproduction.

2. **Warm/cache state**
   - Packed CDB loading is cheap.
   - LSI full-row materialization was removable.
   - Point-location prepare was a measured setup cost.

3. **Prepared-hot replay state**
   - LSI replay is ~millisecond-level.
   - PIP hot traversal is about `1.1s` for the representative workload.
   - The largest remaining hot-body phase is output-chain construction, not
     file I/O and not LSI replay.

Collapsing these states into one label caused the branch confusion.

## Corrected Branch Decision

### Immediate Branch

For the current prepared-hot target:

```text
selected_branch: Branch A
reason: measured hot-body bottlenecks are writer chain construction, app-layer
        continuation/bookkeeping, and prepared/session setup amortization.
```

The next implementation target should be:

```text
structural output-chain construction / compiled partner-assisted chain loop
```

with these constraints:

- preserve AuthorOfficial byte equality;
- do not change RTDL LSI/PIP semantics;
- do not add a RayJoin-specific kernel to RTDL core;
- keep the work app-layer unless it is later generalized into a reusable
  continuation primitive;
- measure against Goal4904/Goal4905 prepared-hot baselines.

### Separate Cold/Setup Branch

For one-off command-line reproduction:

```text
separate_branch: generic point-location preparation persistence / setup reduction
```

This is real, but it is not the same target as prepared-hot replay. It should be
tracked separately to avoid mixing cold-start product usability with hot-query
runtime performance.

### Long-Term Branch

For approaching the author's fused C++/CUDA/OptiX hot kernel:

```text
long_term_branch: data-flow-to-traversal fusion / in-traversal pushdown
```

This remains the architectural direction from the post-v2.14 charter. It is not
unlocked by Goal4906. It requires a separate design and proof that the work is a
generic language/runtime feature rather than a RayJoin-only callback substitute.

## What Goal4906 Supersedes

This goal supersedes the use of Goal4888's
`native_rt_traversal_dominated` label as the prepared-hot branch gate.

It does **not** erase Goal4888. Goal4888 remains useful as:

- the reason Goal4887 was correctly blocked;
- evidence that a coarse phase bucket can mislead if cold/setup and hot/replay
  states are mixed;
- a reminder that any future deeper fusion project must measure candidate/work
  counts and in-kernel behavior, not assume compiler magic.

## Next Goal

The next engineering goal should be:

```text
Goal4907 — Structural Output-Chain Construction Probe
```

Purpose:

- reduce the current prepared-hot writer/chain-loop bottleneck measured in
  Goal4905;
- use Numba or another partner only for app-layer chain descriptor computation
  or face/point-id bookkeeping;
- leave final text emission and exact output bytes verifiable;
- compare against Goal4904/Goal4905 prepared-hot baselines.

Initial acceptance bar:

| Metric | Required |
|---|---|
| Correctness | byte-identical SHA `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| Writer phase | improve over Goal4905 `2.674s` |
| Hot body | improve over Goal4904/Goal4905 `~4.6-4.8s` |
| Scope | app-layer or generic continuation only; no RTDL core RayJoin shortcut |
| Honesty | if speedup is small, record `correct_but_small_win` and stop file-I/O tuning |

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid action would be to keep using Goal4888's cold-state
   `native_rt_traversal_dominated` label after Goal4896-4905 produced a
   prepared-hot sequence that clearly moves the bottleneck.

2. **What actions made or would make the decision stupid?**

   Treating "native traversal dominated" as a universal truth rather than a
   state-specific measurement would be the error. Mixing cold setup, warm cache,
   and prepared-hot replay into one branch decision is exactly how the previous
   V3 work drifted.

3. **Is there another possibility that avoids being stuck?**

   Yes. Split the product into states:

   - cold single-run;
   - warm cache;
   - prepared-hot replay;
   - long-term fused kernel.

   Then optimize the measured bottleneck in the state we are actually targeting.

4. **Can I start a different path that truly solves the problem?**

   Yes. The immediate path is Goal4907, focused on structural output-chain
   construction, because Goal4905 shows file I/O is tiny and Python chain loops
   are now the largest prepared-hot bottleneck.

## Non-Authorization

Goal4906 does not authorize:

- broad RTDL/RayJoin speedup claims;
- a full Section 5.7 eight-pair performance claim;
- claiming that RTDL beats AuthorOfficial overall;
- changing correctness/comparator boundaries;
- adding RayJoin-specific RTDL core kernels;
- resurrecting V3/V4 release claims;
- treating prepared-hot wins as cold single-run wins.
