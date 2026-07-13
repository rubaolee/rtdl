# Goal4834 - RayJoin Patched-Author SoS Contract And Synthetic Gate Plan

Date: 2026-06-30

Status: `goal4834_plan_written_pending_user_or_external_review`

## Purpose

Goal4834 exists to stop the RayJoin reproduction line from wasting more time on
large, ambiguous runs before the exact point-location contract is proven.

The immediate task is to put the author program and RTDL under the same
deterministic directed-segment point-location contract, then prove that contract
with small, discriminating synthetic cases before returning to public-sample or
Section 5.7 data.

This goal does not start implementation. It defines the next implementation
work and its gates.

## Why This Goal Is Needed

The RayJoin paper and source show that Section 5.7 polygon overlay depends on:

1. LSI;
2. vertex point-location / PIP;
3. midpoint point-location / PIP;
4. output-chain assembly.

The recent work exposed two correctness-sensitive places:

- OptiX PIP equal-height candidates can be pruned before the shader's internal
  slope comparison sees all candidates. The author-provided clarification fixes
  this by encoding the slope-based SoS preference into `t_reported`.
- RTDL's overlay helper also exposed a separate continuation data-model bug:
  midpoint point-location faces must be stored per directed map, not in one
  shared field that can be overwritten.

The author clarification should be treated as a semantic patch to the author
program's PIP contract. Therefore a fair comparison should not compare repaired
RTDL against an unpatched author binary when the measured question depends on
this contract.

## Goal-Level Decision Audit

1. **Am I being foolish?**

   The foolish path would be to run large County x Zipcode or Block x Water jobs
   while the PIP tie contract remains ambiguous.

2. **What would make the decision foolish?**

   - Using the old author commit as the final denominator after acknowledging
     the author-provided deterministic `t_reported` patch.
   - Claiming a broad correctness/performance result before synthetic cases
     prove the equal-height tie behavior.
   - Debugging giant outputs first, then trying to infer the semantic contract
     from millions of records.

3. **Is there another path that avoids being stuck on one wrong idea?**

   Yes. Build small synthetic cases that isolate exactly the equal-height
   boundary event and midpoint face ownership event. These cases are cheap,
   explanatory, and falsifiable.

4. **Can I start a different path that actually solves the problem?**

   Yes. First align author-patched and RTDL semantics on synthetic data; only
   then run the public sample and any larger Section 5.7 pair.

## Scope

### In Scope

- Read the RayJoin paper, author source, and author clarification as the
  controlling contract.
- Create a minimal author-source patch that implements the author's clarified
  deterministic `t_reported` rule without changing the overlay algorithm.
- Align RTDL's directed-segment point-location contract with the same rule.
- Build focused synthetic tests that distinguish:
  - larger-slope vs smaller-slope tie choice;
  - `query_map_id == 0` vs `query_map_id == 1`;
  - equal-height candidates with different primitive order;
  - endpoint exclusion / SoS boundary behavior;
  - midpoint face ownership per directed map.
- Run the smallest public author sample only after synthetic correctness passes.
- Run performance only after correctness passes for both patched-author and
  RTDL.

### Out Of Scope

- No Embree work.
- No V3/V4 resurrection.
- No broad Section 5.7 performance claim.
- No eight-pair claim unless exact inputs and answer files exist.
- No large-data debugging before the synthetic gate passes.
- No hidden RayJoin-only native shortcut.

## Contract Choice

Goal4834 chooses the author-clarified intended deterministic behavior as the
RTDL product contract.

The old author commit remains useful as a historical diagnostic baseline, but it
is not the final semantic denominator for deterministic PIP because the author
clarification explains how equal-height OptiX candidates must be reported:

```text
norm_slope = (atan(slope) + pi/2) / pi

query_map_id == 0: prefer larger slope
query_map_id == 1: prefer smaller slope

t_reported = t_edge + max(t_edge, 1.0) * (1.0 - tie_breaker) * 1e-14
```

The exact sign/direction must be verified against:

- the author's clarification;
- the author's source comments and conditions;
- focused synthetic cases where the correct edge is obvious.

If those sources conflict, the conflict must be recorded explicitly and resolved
before performance.

## Work Plan

### Step 1 - Contract Re-Read And Patch Spec

Read again and quote the controlling lines from:

- `C:\Users\Lestat\Downloads\ics24 (1).pdf`;
- `/workspace/RayJoin_fresh` via `git show HEAD:<file>`, not dirty files;
- `C:\Users\Lestat\Downloads\rayjoin_pip_determinism_summary.md`;
- RTDL's current `src/native/optix/rtdl_optix_core.cpp`;
- RTDL's current `src/rtdsl/rayjoin_overlay.py`.

Deliverable:

- `history/internal_docs/goal4834_contract_alignment_notes_2026-06-30.md`

Required content:

- exact author-source line references for PIP tie selection;
- exact author-clarification formula;
- exact RTDL implementation locations;
- explicit statement of any source/comment/clarification tension.

### Step 2 - Patched-Author Minimal Patch

Create a patch against the author source that only changes deterministic PIP hit
reporting:

- no overlay algorithm changes;
- no output-chain changes;
- no data-format changes;
- no timing instrumentation except necessary build/report metadata;
- compatibility fixes may be isolated separately from the SoS semantic patch.

Deliverables:

- `history/internal_docs/goal4834_author_sos_t_reported.patch`
- `history/internal_docs/goal4834_author_patch_scope.md`

Acceptance criteria:

- patch touches only the necessary author PIP source area unless separately
  justified;
- reviewer can see exactly which lines are semantic and which, if any, are
  build compatibility.

### Step 3 - RTDL Contract Alignment

Align RTDL's directed-segment point-location implementation with the same
contract:

- internal equal-height comparison and `t_reported` perturbation must prefer the
  same candidate;
- no RayJoin-only hidden kernel;
- changes must be framed as a directed-segment point-location / SoS contract
  repair;
- keep the existing per-map midpoint face repair if still required.

Allowed RTDL code areas, if needed:

- `src/native/optix/rtdl_optix_core.cpp`;
- `src/rtdsl/rayjoin_overlay.py`;
- focused tests under `tests/`.

Any additional product-code file requires explicit justification in the goal
report.

### Step 4 - Synthetic Data Gate

Create small discriminating synthetic tests before any large run.

Minimum cases:

1. two equal-height boundary candidates, different slopes, `query_map_id == 0`;
2. same geometry with reversed primitive/input order;
3. two equal-height boundary candidates, different slopes, `query_map_id == 1`;
4. endpoint exclusion case;
5. midpoint face ownership case where map0 and map1 midpoint classifications
   differ and must not overwrite each other.

Deliverables:

- `history/internal_docs/goal4834_synthetic_cases.md`
- synthetic test code under `tests/` or a clearly named script if unit tests are
  not practical;
- JSON evidence:
  `history/internal_docs/goal4834_synthetic_gate_summary.json`

Acceptance criteria:

- patched-author and RTDL agree on the chosen edge/face for each synthetic case;
- reversed primitive/input order does not change the deterministic result;
- midpoint per-map ownership remains correct;
- failures stop the goal before public-sample or performance runs.

### Step 5 - Public Sample Correctness

Only after Step 4 passes:

- run patched-author on the author public County x Soil sample;
- run RTDL on the same sample;
- compare both to the author answer where applicable;
- record byte equality, SHA256, chain count, face count, and artifact paths.

Deliverable:

- `history/internal_docs/goal4834_public_sample_correctness_summary.json`

Acceptance criteria:

- patched-author reproduces the author answer or any difference is explained as
  a deterministic author-patch output-contract change;
- RTDL matches the selected denominator output byte-for-byte, or the mismatch is
  diagnosed before performance.

### Step 6 - Controlled Performance Smoke

Only after Step 5 passes:

- compare patched-author vs RTDL on the public sample;
- record machine, GPU, driver, build commit, input size, warmup/repeat policy,
  raw times, median, and ratio;
- do not extrapolate to full Section 5.7.

Deliverable:

- `history/internal_docs/goal4834_public_sample_patched_author_performance.json`

Acceptance criteria:

- correctness remains true for every timed run;
- performance is reported only as a bounded public-sample smoke.

## Exit Labels

- `goal4834_pass_synthetic_gate_and_public_sample_ready_for_review`
- `goal4834_pass_synthetic_gate_but_public_sample_mismatch_diagnosed`
- `goal4834_blocked_by_author_contract_ambiguity`
- `goal4834_blocked_by_rtdl_core_capability_gap`
- `goal4834_fail_redo_due_to_rayjoin_specific_shortcut`

## Review Gate

Goal4834 must end with a call-for-review packet before any larger Section 5.7
pair or performance claim is authorized.

Required reviewer questions:

1. Did the work correctly treat the author clarification as a semantic patch,
   not just prose?
2. Did the author patch avoid algorithm changes outside deterministic PIP
   reporting?
3. Did RTDL implement the same directed point-location contract without adding a
   RayJoin-only shortcut?
4. Did synthetic cases actually distinguish the tie-break direction and
   traversal-order issue?
5. Did public-sample correctness pass before performance?
6. Are all performance numbers bounded to the tested sample and denominator?

## Non-Authorization

This goal does not authorize:

- broad RayJoin paper reproduction claims;
- large Section 5.7 runs before synthetic correctness passes;
- performance before correctness;
- unreviewed public documentation changes;
- V3/V4 work;
- Embree work;
- app-specific hidden native kernels.
