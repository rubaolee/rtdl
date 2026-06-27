# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Feasibility

Date: 2026-06-20

Status: accepted as feasibility analysis, not M7 promotion.

This is not V3 release authorization.

## Scope

Bounded goal:

```text
Evaluate whether grouped_reduction can become the first focused Phoenix V3 M7
performance row, using existing 262,144-row and 524,288-row RayDB-style
grouped-reduction evidence with repeat-aware hot/cold amortization.
```

Primary packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.json
```

Generator and tests:

```text
scripts/v3_phoenix_grouped_reduction_m7_feasibility.py
tests/v3_phoenix_grouped_reduction_m7_feasibility_test.py
```

## External Review

External reviewer:

```text
Claude (claude-sonnet-4-6)
```

Review file:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_feasibility_review_2026-06-20.md
```

Claude verdict:

```text
approve-with-required-fixes
P0 issues: 0
P1 issues: 5
2ai_consensus_authorized: true after P1 fixes
```

Claude independently verified the amortization math for all four rows:

| Scale | Mode | Hot speedup | Break-even | Repeat 1 end-to-end | Repeat 100 end-to-end |
| --- | --- | ---: | ---: | ---: | ---: |
| 262,144 | count | 9.863861x | 1 | 18.080719x | 16.458010x |
| 262,144 | sum | 202.773996x | 1 | 1.624894x | 3.114570x |
| 524,288 | count | 8.751652x | 18 | 0.592304x | 2.579191x |
| 524,288 | sum | 158.010302x | 1 | 1.019809x | 1.972766x |

## Required Fixes Applied

P1 fixes applied before this consensus:

1. The Markdown summary now displays a case-specific main blocker, so
   `524288/count` surfaces `single_query_end_to_end_not_optix_win`.
2. Tests now pin the favorable `262144/count` case:
   `break_even_repeat_count_ceiling == 1` and repeat-1 end-to-end speedup
   above 15x.
3. Markdown release/public/whole-app flags are derived from the JSON payload,
   not hardcoded literal strings.
4. The packet now records Embree and OptiX workload-build times separately,
   uses max workload-build cost to flag large sum setup, and includes both
   `262144/sum` and `524288/sum` in the large-cold-cost summary.
5. The packet records source warmup asymmetry: `262144` used warmup=1 and
   `524288` used warmup=2.

## Evidence Accepted

The packet is accepted only as:

```text
grouped_reduction_m7_feasibility_not_promoted
```

Accepted facts:

- grouped_reduction is a strong reusable V3 performance candidate;
- all four source pairs match CPU reference;
- OptiX hot prepared-query time is faster than Embree in all four pairs;
- 262,144/count is favorable even at repeat=1;
- 524,288/count loses at repeat=1 and needs repeat amortization;
- 524,288/sum has a 158x hot-query ratio, but repeat=1 end-to-end is only
  about 1.020x;
- 262,144/sum and 524,288/sum both have large workload-build cost on at least
  one backend path;
- cross-scale comparisons are feasibility inputs, not standardized scale
  ladder timing, because the source warmups differ.

## Verification

Focused tests after P1 fixes:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_m7_feasibility_test tests.v3_release_wording_gate_test
8 tests OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
24 modules / 94 tests OK
```

Note: local Python still prints `Could not find platform independent libraries
<prefix>` before test output, but the commands exit 0 and the suites pass.

## Consensus Decision

Codex accepts Claude's review and the required fixes as complete.

Grouped reduction should not be promoted to M7 yet. The next valid promotion
step is not more wording; it is a fresh M7-designated rerun and public prepared
query contract that makes setup, warmup, repeat count, and amortization rules
first-class.

This bounded packet is not:

- V3 release authorization;
- a public speedup claim;
- a whole database speedup claim;
- a claim that RayDB-style V3 is 158x faster end to end;
- an M7-qualified release row.

## Goal-Level Decision Audit

Decision: close grouped_reduction as feasibility-not-promoted after Claude
review, P1 fixes, and verification.

1. Was I foolish?

   No. The decision is bounded and refuses promotion despite strong hot-query
   signals.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to turn the 158x hot-query ratio into an
   end-to-end or whole-database claim. This packet blocks that reading.

3. Was there another path?

   Yes. I could have tried to write public docs around the hot ratios directly.
   That would have repeated the old overclaim pattern.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is a real M7 prepared-query contract and fresh rerun:
   setup, warmups, repeat counts, cold cost, and hot query timing must be
   presented together.
