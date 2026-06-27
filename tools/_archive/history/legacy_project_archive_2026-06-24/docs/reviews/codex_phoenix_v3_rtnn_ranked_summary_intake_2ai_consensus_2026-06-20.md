# Codex 2-AI Consensus: Phoenix V3 RTNN Ranked-Summary Candidate Intake

Date: 2026-06-20

Status: bounded RTNN intake packet closed as reviewed internal candidate
evidence only.

This is not V3 release authorization, not RTNN M7 row qualification, and not
public RTNN acceleration or paper-reproduction wording.

## Inputs

External review:

```text
docs/reviews/claude_phoenix_v3_rtnn_ranked_summary_intake_review_2026-06-20.md
verdict: approve-with-required-fixes
P0 findings: none
P1 findings: two clarity/guard fixes
```

Review request:

```text
docs/reviews/call_for_review_phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md
```

Primary evidence:

```text
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
```

## Claude Review Result

Claude approved the intake after P1 fixes and found no P0 blockers.

Required P1 fixes:

1. Replace the undefined `boundary row` table label with consistent internal
   candidate wording.
2. Make claim-boundary checking fail if required false claim flags are absent,
   instead of treating missing flags as falsy.

Both P1 items were fixed before this consensus was written.

Additional hardening:

- added `no_multi_run_variance_evidence` to M7 blockers;
- added a table note that wall ratios below 1.0 mean OptiX is slower than
  Embree;
- added tests that required claim-boundary flags are present.

## Verified Facts

Accepted internal facts:

```text
status: internal_rtnn_ranked_summary_candidate_not_m7
generic_capability: ranked_summary
generic_capability_status: distribution_specific_candidate_wall_regression
row_count: 6
group_count: 3
all_rows_ok: true
all_same_contract: true
all_same_metric_source: true
all_aggregate_summaries_match: true
all_claim_flags_blocked: true
all_hot_optix_faster_than_embree: true
all_wall_optix_slower_than_embree: true
release_authorized: false
public_speedup_claim_authorized: false
m7_qualified: false
```

Rows:

| Distribution | Hot OptiX / Embree | Wall OptiX / Embree | Boundary |
| --- | ---: | ---: | --- |
| clustered | 3.333x | 0.625x | internal candidate only |
| shell | 1.182x | 0.316x | internal candidate only |
| uniform | 1.084x | 0.303x | internal candidate only |

The wall ratios are intentionally recorded because OptiX loses the wall metric
on all three rows. Any release-row promotion must solve or characterize that
gap.

## Verification

Focused RTNN test:

```text
py -3 -m unittest tests.v3_phoenix_rtnn_ranked_summary_intake_test
Ran 5 tests
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

Full V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 22
Ran 81 tests
OK
```

The local Python installation prints `Could not find platform independent
libraries <prefix>` before these runs, but the commands return success and the
test bodies pass.

## Codex Consensus

Codex agrees with Claude's post-fix verdict.

The RTNN packet may be accepted only as reviewed internal candidate evidence
because:

- it extracts real 65,536-point ranked-summary rows from the all-app calibrated
  artifact;
- Embree and OptiX rows use the same exact fixed-radius ranked-summary
  contract per distribution;
- aggregate summaries match between backends;
- all required public/release/paper/zero-copy claim flags are explicitly
  present and false where required;
- hot elapsed OptiX rows beat Embree rows, strongest on clustered data;
- wall timing is slower for OptiX on all three distributions and remains a
  blocker;
- the result is distribution-specific and not universal RTNN acceleration.

## Closure Boundary

This bounded RTNN intake closes only at this level:

```text
reviewed internal candidate evidence: accepted
ranked_summary M7 row: no
V3 release authorization: no
public speedup wording: no
universal RTNN acceleration: no
paper reproduction claim: no
Phoenix M7-qualified release rows: 0
```

Future RTNN work should either keep this packet internal or build a real M7 row
packet that resolves the blockers:

- wall timing slower than Embree;
- distribution-specific evidence;
- no multi-run variance evidence;
- summary-row materialization;
- no author-code or external ANN baseline;
- prepared CUDA graph replay not present;
- fresh row-level public review missing.

## Goal-Level Decision Audit

Decision: close the RTNN focused intake as reviewed internal candidate evidence
after Claude review and P1 fixes.

1. Was I foolish?

   The corrected closure decision is not foolish. It preserves the hot-row
   signal while making the wall-time blocker unavoidable.

2. If yes, what actions made the decision foolish?

   The foolish risk was using the clustered 3.333x hot result without equally
   foregrounding that OptiX loses wall timing on every RTNN row.

3. Was there another path?

   Yes. I could have rerun the pod or promoted the all-app row directly. Both
   would skip the classification gap.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path classifies RTNN honestly and leaves the next work as
   concrete engine/performance repair, not wording.
