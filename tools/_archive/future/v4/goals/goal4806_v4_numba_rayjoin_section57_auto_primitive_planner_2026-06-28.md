# Goal4806 - V4 + Numba RayJoin Section 5.7 Auto-Primitive Planner

Date: 2026-06-28

Status: externally reviewed by Antigravity; `approve_with_required_amendments`

## Objective

Build a V4.0 research/product candidate for the RayJoin paper-reproduction suite, focused on Section 5.7 Polygon Overlay, where the user writes the workload semantics and chooses `partner="numba"`, while RTDL/V4 automatically enumerates valid primitive combinations, validates correctness, measures them on the target NVIDIA GPU, and selects the fastest valid route.

The user must not need to know names such as AABB index, any-hit, bounded witness, grouped reduction, or polygon-refinement primitive names in order to get the best route. Those names may appear in the audit output, but not as required user knowledge.

## Why This Goal Exists

This goal tests whether V4 is a real language/runtime layer rather than a bag of hand-picked primitives. It also tests whether the Numba partner story can support a serious paper-reproduction workload rather than only isolated tutorial surfaces.

The desired user story is:

```python
from rtdsl import v4 as rtdl

result = rtdl.paper.rayjoin.section57_polygon_overlay(
    dataset_root="data/rayjoin_section57_cdb",
    partner="numba",
    select="fastest_valid",
)
```

The runtime should then plan, compile or bind available primitives, measure candidate plans, choose the best valid route, and emit a complete evidence packet.

## Scope

In scope:

- RayJoin Section 5.7 Polygon Overlay workload.
- V4 public paper-reproduction entrypoint or maintainer-facing candidate entrypoint if the route is not release-ready.
- Numba as an explicit partner for continuation, refinement, reduction, or plan-local GPU kernels where Numba is appropriate.
- RTDL/V4 automatic primitive-plan enumeration and selection.
- Fair comparison against the existing V2.14 exact-suite route on the same Section 5.7 contract.
- Author-code correctness and performance comparison when the RayJoin author source/binaries and exact or same-source regenerated inputs are available.
- Correctness, timing, phase breakdown, candidate-plan scoreboard, selected-plan explanation, and rejection reasons for slower or invalid routes.

Out of scope:

- Teaching polygon overlay as an application algorithm.
- Requiring the user to hand-select primitive names.
- Claiming a full paper reproduction without all required Section 5.7 inputs and author binary evidence.
- Claiming high performance from toy or synthetic-only inputs.
- V4.1 arbitrary ray-action callback work. This goal may use Numba for bounded partner kernels, but arbitrary OptiX callback/code injection remains outside V4.0.

## External Review Amendments Required Before Execution

Antigravity reviewed this goal and returned `approve_with_required_amendments`.
Implementation must obey these amendments:

1. **Numba must be real JIT partner work.** Numba stages must use `numba.cuda.jit`
   to compile Python logic such as predicates, filters, compaction, or
   aggregators into GPU kernels. Wrapping precompiled C++/CUDA routines does not
   count as Numba partner work.
2. **Numba must operate on device-resident arrays.** The evidence must show that
   the Numba stage consumes GPU-resident columns produced by the RTDL/V4 route,
   without hidden hot-path host materialization.
3. **Numba must stay outside OptiX traversal.** V4.0 may use Numba before or
   after native traversal/refinement stages, but must not inject dynamic callback
   code into the OptiX shader/ray-intersection loop. That remains V4.1 scope.
4. **Correctness must be topology-aware.** Section 5.7 correctness must validate
   reconstructed overlay geometry/topology using coordinate or structural hashes,
   not only row counts.
5. **The planner scoreboard must include compile/JIT costs.** Candidate evidence
   must list evaluated and skipped routes, skip reasons, compile/JIT overheads,
   phase timings, and final selected-plan rationale.

## Plan

### Step 1 - Re-read Existing RayJoin Assets

Inventory the current public and archived RayJoin implementation surfaces:

- `examples/paper_reproduction/rayjoin.py`
- `src/rtdsl/rayjoin_paper_suite.py`
- existing V2.14 RayJoin exact-suite route in the archive/current source
- existing Section 5.7 matrix runner and dataset contract
- existing V4 operator surfaces that can participate in broadphase, refinement, witness collection, or reduction

Output: a short implementation map naming which code paths are reusable and which are missing.

### Step 2 - Define the Semantic User Entry

Create or extend a user-level entrypoint that expresses Section 5.7 as a semantic workload request:

- dataset root
- pair selection
- partner choice: `numba`
- selection policy: `fastest_valid`
- optional measurement controls: warmup, repeats, output directory

The entrypoint must not require primitive names. It may expose a diagnostic flag to print candidate plans.

Output: runnable command and Python API sketch.

### Step 3 - Build Candidate Plan Enumeration

Add a planner that generates available primitive combinations for the workload. Candidate plans should include, as available:

- broadphase candidate pair generation;
- ray/segment/polygon predicate refinement;
- Numba continuation or reduction kernels;
- RTDL-native fallback continuation where Numba is not valid;
- V2.14-compatible baseline route for comparison.

Every candidate plan must declare:

- semantic contract;
- required input layout;
- primitive/operator stages;
- partner stages;
- expected output schema;
- correctness comparator;
- reasons it may be skipped.

Output: machine-readable candidate plan list.

### Step 4 - Implement Numba Partner Candidate(s)

Implement the Numba-backed candidate kernels needed for the first serious plan. The implementation must be generic at the operator/continuation level, not a hidden app-identity kernel named after RayJoin.

Acceptable Numba roles include:

- refining candidate rows with bounded polygon/segment predicates;
- compacting or grouping valid hit rows;
- reducing overlay-related counters or witness summaries;
- assembling plan-local result columns after RTDL candidate generation.

The Numba implementation must use `numba.cuda.jit` and run on device-resident
arrays. It must not call back into OptiX traversal or wrap a precompiled backend
routine while pretending to be a Numba partner implementation.

Output: at least one end-to-end V4+Numba candidate plan that can run on the Section 5.7 contract, with an explicit Numba JIT kernel stage and device-residency evidence.

### Step 5 - Correctness Gate

Run correctness before performance credit:

- V4+Numba selected plan versus V2.14 exact-suite output on the same input/pair contract;
- author-code route comparison when author source/binaries and exact or same-source regenerated inputs are available;
- topology-aware output validation using coordinates, chain structure, or stable structural hashes;
- record status for every pair, not just one success row.

Output: correctness table with pass/fail, row counts, topology/geometry hashes or comparable summaries, and mismatch diagnostics.

If the author implementation cannot be built or run, the goal must record
`blocked_missing_author_baseline` for the author-comparison column. That does
not block V4-versus-V2.14 engineering work, but it blocks any full
paper-reproduction claim.

### Step 6 - Performance Selection Gate

On NVIDIA GPU, run candidate-plan selection with:

- warmup and repeated measurements;
- phase timings;
- selected-plan timing;
- rejected-plan timing or skip reason;
- Numba compile/JIT overhead separated from steady-state execution;
- V2.14 timing under the same contract;
- author-code timing under the same Section 5.7 contract when available.

Output: candidate scoreboard and selected plan.

The evidence packet must keep three timing/correctness columns separate:

1. `author_code`
2. `v2_14_exact_suite`
3. `v4_numba_selected_plan`

Rows without a valid author-code measurement must be visibly labeled
`blocked_missing_author_baseline`, not omitted.

### Step 7 - Evidence Packet and User Readout

Write a final evidence packet:

- user command/API used;
- candidate plans considered;
- selected primitive combination;
- correctness results;
- phase timing breakdown;
- V4+Numba versus V2.14;
- author comparison when available;
- claim classification: `high_performance`, `parity`, `regression`, `blocked_missing_inputs`, or `not_release_ready`.

## Evaluation Criteria

### Required to Call the Goal Complete

1. **User-level semantics are real.** The public command/API accepts Section 5.7 semantics and `partner="numba"` without requiring primitive names.
2. **Automatic selection is real.** The system enumerates more than one candidate route or explicitly records why only one valid route exists. The selected route must come from measured candidate evidence, not a hardcoded default.
3. **Correctness comes first.** No speedup may be counted unless the route passes the Section 5.7 correctness comparator against the V2.14 exact-suite contract for the same pairs and dataset root.
4. **Numba is doing meaningful partner work.** The evidence must identify which `numba.cuda.jit` stage is Numba-backed, which device arrays it consumes, and why it is not just a Python wrapper around an old path.
5. **No toy result can satisfy the goal.** Toy or fixture runs may be used for development, but the completion evidence must be from real Section 5.7 inputs or must end with `blocked_missing_inputs`.
6. **The evidence is reproducible.** Commands, dataset labels, commit hash, GPU identity, warmup/repeat policy, and output paths are recorded.
7. **No V4.1 callback scope creep.** The implementation must not inject arbitrary Numba/user callback logic into OptiX traversal.
8. **Author-code comparison is explicit.** A complete paper-reproduction claim
   requires correctness and performance comparison against the RayJoin author
   implementation. If the author baseline cannot be run, the result must say so
   directly and cannot be marketed as a full paper reproduction.

### High-Performance Bar

The goal may classify the result as `high_performance` only if all are true:

- correctness passes for all measured Section 5.7 pairs;
- V4+Numba selected route beats the V2.14 exact-suite route by at least `1.20x` geomean on the measured real Section 5.7 pair set;
- no measured pair regresses below `0.98x` unless the evidence explicitly classifies that pair as a control row and excludes it before the run;
- the selected route is chosen by the automatic selector from candidate measurements;
- phase timing shows the improvement comes from a V4/Numba runtime/primitive-plan choice, not from different inputs, fewer outputs, skipped correctness work, or a warmed cache asymmetry.
- author-code timing/correctness is reported, or the result is explicitly
  downgraded from full paper reproduction to V4-versus-V2.14 engineering
  evidence with `blocked_missing_author_baseline`.

### Parity or No-Go Outcomes

If correctness passes but speedup is below the high-performance bar, the correct outcome is `parity` or `not_release_ready`, not inflated wording.

If correctness fails, the goal remains incomplete until fixed or is closed as `no_go_correctness_failed`.

If exact Section 5.7 inputs or author binaries are missing, the goal may produce a useful implementation packet, but it must not claim full paper reproduction.

## External Review Questions

Ask the reviewer to answer:

1. Is the goal clear and executable?
2. Does it correctly require user-level semantics instead of primitive-name hand selection?
3. Is the automatic primitive-plan selection requirement strong enough?
4. Is Numba partner work defined in a way that is meaningful and not just wrapper theater?
5. Are the correctness and performance bars fair and not toy-level?
6. Are the no-go and bounded-claim outcomes explicit enough?
7. Does anything in this plan accidentally pull V4.1 arbitrary callback work into V4.0?

## Non-Authorization

This goal proposal does not authorize a V4.0 high-performance claim, a full RayJoin Section 5.7 paper-reproduction claim, or a new public release tag. It only authorizes implementation after external review accepts or amends the plan.
