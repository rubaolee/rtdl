# Codex 2-AI Consensus: Phoenix V3 RayDB M28 Grouped-Reduction Evidence

Date: 2026-06-20

Status: bounded RayDB M28 evidence goal closed as internal generic
grouped-reduction evidence only.

This is not V3 release authorization, not M7 row qualification, and not public
database acceleration wording.

## Inputs

External review:

```text
docs/reviews/claude_phoenix_v3_raydb_m28_grouped_reduction_evidence_review_2026-06-20.md
verdict: approve-with-required-fixes
P0 findings: none
P1 findings: four documentation/test hardening fixes
```

Review request:

```text
docs/reviews/call_for_review_phoenix_v3_raydb_m28_grouped_reduction_2026-06-20.md
```

Primary evidence:

```text
docs/rebuild/v3/phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_524288.json
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/overlarge_1048576_attempt_status.txt
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_1048576.log
```

Gemini fallback was attempted, but the local Gemini CLI returned an
`IneligibleTierError`. Claude therefore supplies the required external-AI side
of the 2-AI consensus.

## Claude Review Result

Claude approved the evidence with required fixes and no P0 findings.

Required P1 fixes:

1. Explain that OptiX `sum` `cold_prepare_total_sec` includes one-time
   ray-batch preparation and is excluded from hot-query median timing.
2. Assert Embree/OptiX `rt_core_accelerated` differentiation in the evidence
   test.
3. Require the preserved overlarge log to contain content, not merely exist.
4. Surface the asymmetric repeat counts in the human-readable report.

All four P1 items were fixed before this consensus was written.

Additional low-risk hardening was also added:

- the report clarifies that `raydb_paper_triangle_scan_*` contract names are
  fixture-domain labels, not RayDB engine invocation;
- the test now asserts the machine-readable `comparison_scope`;
- the test now checks count-row setup remains light.

## Verified Commands

Focused RayDB evidence test:

```text
py -3 -m unittest tests.v3_phoenix_raydb_m28_evidence_test
Ran 4 tests
OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

Combined wording/RayDB regression test:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_raydb_m28_evidence_test
Ran 6 tests
OK
```

Full V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 20
Ran 71 tests
OK
```

The local Python installation prints `Could not find platform independent
libraries <prefix>` before these runs, but the commands return success and the
test bodies pass.

## Codex Consensus

Codex agrees with Claude's post-fix verdict.

The RayDB M28 packet may be accepted as internal Phoenix V3 evidence for the
generic `grouped_reduction` capability because:

- it uses the same app-agnostic RTDL grouped i64 reduction primitive across
  Embree and OptiX;
- the 524,288-row / 2,048-group row is non-toy;
- CPU reference parity passes on all rows;
- Embree rows are non-RT-core and OptiX rows are RT-core accelerated;
- prepared steady-state, ray-batch reuse, and primitive-payload reuse are
  explicitly recorded;
- no partner continuation is required;
- no SQL engine, query planner, transaction system, or app-specific native
  engine logic is introduced;
- the 1,048,576-row overlarge attempt is preserved as a negative/over-budget
  artifact instead of hidden;
- hot-query timing is separated from 213s+ setup/cold-prepare costs;
- all public/release claim flags remain false.

Allowed interpretation:

```text
For this generated RayDB-style grouped-reduction row, the prepared hot-query
OptiX route is faster than Embree after workload and prepared state already
exist.
```

Forbidden interpretation:

```text
V3 RayDB is 158x faster end to end.
```

## Closure Boundary

This bounded RayDB M28 goal is closed only at this level:

```text
internal generic grouped-reduction evidence: accepted
M7-qualified release row: no
V3 release authorization: no
public speedup wording: no
whole-app/database acceleration claim: no
paper reproduction claim: no
true zero-copy claim: no
Phoenix M7-qualified release rows: 0
```

The next Phoenix step should continue capability-first work: choose the next
generic V3 capability gap, not the largest historical speedup row.

## Goal-Level Decision Audit

Decision: close RayDB M28 as internal grouped-reduction evidence after Claude
review and P1 fixes.

1. Was I foolish?

   The corrected closure decision is not foolish. It is bounded, externally
   reviewed, and keeps all release/public claims blocked.

2. If yes, what actions made the decision foolish?

   The foolish actions during execution were using the wrong Claude invocation
   twice before returning to the historical working pattern, and initially
   accepting an empty overlarge log as sufficient.

3. Was there another path?

   Yes. I could have skipped external review, or waited on a broken Claude path,
   or treated the hot-query ratio as a release result. Those would repeat the
   old failure mode.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path keeps RayDB M28 as one reviewed internal capability
   brick and moves Phoenix toward the next generic V3 capability only after
   evidence, tests, and external review are aligned.
