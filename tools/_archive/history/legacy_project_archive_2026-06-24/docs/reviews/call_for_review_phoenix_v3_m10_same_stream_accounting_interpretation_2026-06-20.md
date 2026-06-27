# Call For Review: Phoenix V3 M10 Same-Stream Accounting Interpretation

Reviewer: Claude or Gemini.

Requested by: Codex Phoenix V3 rebuild workstream.

Date: 2026-06-20.

## Review Target

Please critically review the new M10 interpretation packet:

```text
docs/rebuild/v3/phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.json
tests/v3_phoenix_m10_same_stream_accounting_interpretation_test.py
```

Source evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m10_same_stream_65536.json
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json
docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md
```

Current local verification:

```text
py -3 -m unittest tests.v3_phoenix_m10_same_stream_accounting_interpretation_test tests.v3_release_wording_gate_test
7 tests OK

py -3 scripts/run_test_matrix.py --group v3_rebuild
32 modules / 141 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
```

## Proposed Interpretation

Codex is proposing this bounded interpretation:

```text
status: m10_same_stream_accounting_interpreted_not_release
raw_index_classification_preserved: pass_internal_with_accounting_warning
raw_index_clean_pass_preserved: false
event_ordering_interpretation: per_sample_event_ordering_clean
median_accounting_interpretation: independent_median_additivity_note
release_authorized: false
public_speedup_claim_authorized: false
same_stream_public_claim_authorized: false
true_zero_copy_public_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

The reason is:

- M10 has two partner rows: CuPy and Numba.
- Each row has five CUDA event samples.
- Every retained sample has `same_stream_ready=true`.
- Every retained sample has `total_event_seconds >= native_event_seconds`.
- Every retained sample has `total_event_seconds >= partner_event_seconds`.
- The only raw warning is the CuPy independent-median additivity warning:
  `median(total_event)` is slightly smaller than
  `median(native_event)+median(partner_event)` by about 0.128 microseconds.
- The raw artifact itself says these medians are computed independently and may
  come from different repeats.

Therefore Codex treats the warning as a methodology note, not as a CUDA
event-ordering failure.

## Review Questions

Please answer directly and critically:

1. Is it correct to preserve the raw M4 classification as
   `pass_internal_with_accounting_warning` while adding an interpretation that
   the retained samples are `per_sample_event_ordering_clean`?
2. Is the phrase `independent_median_additivity_note` technically fair for the
   CuPy warning?
3. Does the packet accidentally imply public same-stream readiness, public
   performance readiness, true-zero-copy readiness, or M7 qualification?
4. Are the tests sufficient to prevent future overclaim or raw-evidence
   rewriting?
5. What P0/P1 fixes are required before this M10 interpretation can be accepted
   as an internal V3 note?

## Expected Verdict Format

Please return:

```text
Verdict: approve / approve-with-fixes / reject
P0 findings:
P1 findings:
Suggested wording changes:
Can this be treated as an internal interpretation note after fixes?
Can it be treated as M7 or public release evidence?
```

The expected answer to the last question may be "no"; that is acceptable.
