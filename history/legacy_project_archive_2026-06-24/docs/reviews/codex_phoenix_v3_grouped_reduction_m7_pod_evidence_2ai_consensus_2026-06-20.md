# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Pod Evidence

Date: 2026-06-20

Status: accepted as fresh post-run intake evidence, not M7 promotion.

This is not V3 release authorization and not public speedup wording.

## Scope

Bounded goal:

```text
Execute and interpret the reviewed fresh M7-designated grouped_reduction pod
rerun, then decide whether the result can be promoted into an M7-qualified V3
release row.
```

Primary report:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.md
```

Pod:

```text
root@213.173.108.14 -p 11592
NVIDIA RTX 4000 Ada Generation
```

## External Review

External reviewer:

```text
Claude (claude-sonnet-4-6)
```

Review file:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_pod_evidence_review_2026-06-20.md
```

Claude verdict:

```text
approve-with-required-fixes
P0 issues: 0
P1 issues: 2
2ai_consensus_authorized: true after P1 fixes
```

Claude independently verified the hot-query ratios, break-even repeat counts,
repeat-1 end-to-end results, and repeat-100 end-to-end results against the raw
fresh evidence JSON files.

## Required Fixes Applied

P1 fixes applied before this consensus:

1. The stale `158x` narrative in
   `goal_level_decision_audit.foolish_actions` was replaced with the actual
   fresh maximum hot-query ratio, `224.269x`.
2. Fresh-rerun pair rows now use
   `claim_status: internal_post_run_intake_not_m7` instead of the stale
   feasibility label.
3. Tests now assert that fresh pairs carry the post-run intake label and that
   the stale `158x` text does not return.

## Evidence Accepted

The fresh pod run is accepted only as:

```text
grouped_reduction_m7_post_run_intake_not_promoted
```

Accepted facts:

- both fresh source files used `warmup=3`;
- pre-run GPU Python, OptiX hardware, claim-boundary, and native build gates
  passed;
- the run completed with `m7_execution.status: 0`;
- all four count/sum scale pairs match the CPU reference;
- all four OptiX hot prepared-query rows are faster than Embree;
- the maximum hot prepared-query speedup is `224.269x`;
- the old 213s+ cold/setup issue is not present in the fresh run;
- count rows still lose at repeat=1 and need about 14 repeats to break even;
- `262144/sum` is near parity but still below 1.0x at repeat=1;
- `524288/sum` wins only marginally at repeat=1, about `1.016x`;
- repeat-100 end-to-end results are strong for sum mode, above 32x.

## Boundary

Claim state remains:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promoted: false
Phoenix M7-qualified release rows: 0
```

This consensus does not authorize:

- V3 release;
- a public V3 speedup claim;
- whole-database or whole-app speedup wording;
- treating the `224.269x` hot-query ratio as an end-to-end result;
- hiding cold/setup cost or repeat count next to hot-query timing;
- M7 promotion before a public prepared-query contract and final public-row
  wording review.

## Verification

Focused tests after Claude P1 fixes:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_m7_pod_evidence_test tests.v3_phoenix_grouped_reduction_m7_feasibility_test tests.v3_release_wording_gate_test
12 tests OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
missing_required_strings: []
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
26 modules / 106 tests OK
```

Note: local Python still prints `Could not find platform independent libraries
<prefix>` before test output, but the commands exit 0 and the suites pass.

## Consensus Decision

Codex accepts Claude's review and the required fixes as complete.

The grouped_reduction fresh evidence is valuable and should be kept as the
strongest current reusable prepared-query candidate. It still does not become
an M7-qualified public V3 row. The next valid promotion path is to write and
review a public prepared-query contract covering fixed schema, setup/cold cost,
warmup, repeat counts, hot windows, and exact artifact reproduction; then run a
final row-level wording review before any release text changes.

## Goal-Level Decision Audit

Decision: close fresh grouped_reduction pod evidence as post-run intake, not
promotion.

1. Was I foolish?

   No. The decision accepts the useful evidence while keeping all release and
   public-claim flags false.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to convert the `224.269x` hot-query
   number into public end-to-end wording, or to ignore the repeat-1 losses.

3. Was there another path?

   Yes. I could have promoted grouped_reduction immediately after the pod run.
   That would repeat the old mistake of letting exciting numbers outrun the
   user contract.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is a public prepared-query contract plus final row-level
   review, or an explicit decision to keep grouped_reduction internal while
   Phoenix V3 moves to the next reusable capability candidate.
