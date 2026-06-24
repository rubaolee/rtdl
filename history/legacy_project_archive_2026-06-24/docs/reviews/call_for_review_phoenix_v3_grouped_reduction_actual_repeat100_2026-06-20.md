# Call For Review: Phoenix V3 Grouped-Reduction Actual Repeat100 Evidence

Reviewer: Claude or Gemini.

Date: 2026-06-20.

## Review Target

Please critically review the actual repeat100 grouped_sum evidence and current
candidate wording:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.json
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.json
tutorials/current/07_grouped_sum_prepared_query.md
tests/v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test.py
```

Raw pod artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_repeat100_actual_20260620
```

## Local Verification

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test tests.v3_phoenix_grouped_reduction_prepared_query_contract_test tests.v3_rebuild_tutorial_surface_test tests.v3_phoenix_grouped_reduction_m7_pod_evidence_test tests.v3_release_wording_gate_test
25 tests OK

py -3 scripts/run_test_matrix.py --group v3_rebuild
32 modules / 142 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
```

## Evidence Summary

The old sum-only packet used modeled repeat100 values. Codex reran the generic
grouped-reduction runner on the pod with actual `repeat=100` for both Embree
and OptiX, sum mode only, warmup=3.

Measured rows:

| Row | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Classification |
| --- | ---: | ---: | ---: | --- |
| 262,144 rows / 1,024 groups | 197.056x | 199.501x | 27.012x | candidate, not M7 |
| 524,288 rows / 2,048 groups | 159.163x | 159.482x | 2.242x | candidate with large cold prepare cost, not M7 |

All rows matched CPU reference and kept public/release flags false.

## Review Questions

1. Is it correct to supersede the modeled 32x/33x repeat100 wording with actual
   repeat100 evidence?
2. Is the 262,144-row cold-plus-loop result strong enough to remain an M7
   candidate after final public-row review?
3. Should the 524,288-row row be downgraded from candidate because cold prepare
   reduces cold-plus-loop speedup to 2.242x?
4. Does the current wording correctly prevent hot-query overclaim, whole-app
   overclaim, and broad V3 speedup claims?
5. What P0/P1 fixes are required before any grouped_sum row can be promoted?

## Expected Verdict Format

Please return:

```text
Verdict: approve / approve-with-fixes / reject
P0 findings:
P1 findings:
Candidate decision:
Suggested wording changes:
Can any row be M7-qualified now?
Can any public speedup wording be published now?
```

Be strict. A "no" answer to the last two questions is acceptable.
