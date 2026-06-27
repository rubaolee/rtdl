# Phoenix V3 M10 Same-Stream Accounting Interpretation

Status: `m10_same_stream_accounting_interpreted_not_release`.

This packet interprets one narrow M10 issue from the Phoenix M4 grouped-
continuation evidence. It is not a release packet and it does not rewrite the
raw evidence.

Source artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m10_same_stream_65536.json
```

Machine-readable packet:

```text
docs/rebuild/v3/phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.json
```

## Bottom Line

M10 still remains internal evidence:

```text
release_authorized: false
public_speedup_claim_authorized: false
same_stream_public_claim_authorized: false
true_zero_copy_public_claim_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_2ai_consensus_status: claude_codex_consensus_complete_internal_not_m7
current_packet_external_review_status: claude_approved_after_p0_p1_fixes_internal_note
```

The raw M4 evidence index still says:

```text
pass_internal_with_accounting_warning
clean_pass: false
```

The interpretation here is narrower:

```text
event_ordering_interpretation: per_sample_event_ordering_clean
median_accounting_interpretation: independent_median_non_additivity_note
```

That means the accounting warning is not treated as a CUDA event-ordering
failure. It is a methodology note about adding independently computed medians.

## What Was Checked

The M10 artifact has two partner rows: CuPy and Numba. Each row has five CUDA
event samples.

For every retained sample:

- `same_stream_ready` is true;
- `total_event_seconds >= native_event_seconds`;
- `total_event_seconds >= partner_event_seconds`.

No retained sample violates those per-sample checks.

| Partner | Samples | Bad samples | Raw accounting status | Interpretation |
| --- | ---: | ---: | --- | --- |
| CuPy | 5 | 0 | `warning` | per-sample clean; independent median note |
| Numba | 5 | 0 | `clean` | per-sample clean |

The CuPy warning is this:

```text
median(total_event) is smaller than median(native_event)+median(partner_event)
```

The measured values are:

| Metric | Seconds |
| --- | ---: |
| median native event | 0.0007828159928321838 |
| median partner event | 0.000005152000114321708 |
| median native plus partner | 0.0007879679929465055 |
| median total event | 0.0007878400087356568 |
| delta total minus native plus partner | -0.00000012798421084868792 |

That delta is about -0.128 microseconds. The warning text already explains the
reason: the medians are computed independently and may come from different
repeats. Therefore this packet treats the warning as an independent-median
non-additivity note, not as proof that the event window is invalid.

The raw Numba evidence records `native_start_event_ptr`,
`native_done_event_ptr`, and `partner_done_event_ptr` as `0`. That is an
instrumentation-surface limitation of the current Numba path: the Numba CUDA
event wrapper used by this packet does not expose stable host-visible event
pointer values like the CuPy path does. The timing interpretation still comes
from recorded CUDA event elapsed times and the retained per-sample checks above.
This remains internal evidence only.

## What This Does Not Prove

This packet does not prove true-zero-copy readiness. The M10 path lacks
transfer-counter evidence, so `true_zero_copy_ready` remains false and
`true_zero_copy_public_claim_authorized` remains false.

This packet also does not make M10 a public same-stream claim. It only prevents
future reviewers from misreading the raw accounting warning as an event-ordering
failure.

The open `phoenix_m4_system_python_missing_cupy_numba` gap also remains: the
evidence was produced in the rebuild venv, while the system-Python CuPy/Numba
binding path is still not closed.

## Hard Boundaries

Do not rewrite the raw M4 evidence index from
`pass_internal_with_accounting_warning` to `clean_pass`.

Do not claim true-zero-copy readiness from M10.

Do not claim same-stream public release wording from this packet.

Do not promote M10 to M7 from this interpretation alone.

Do not use M10 as public performance evidence.

## Remaining Blockers

- `transfer_counter_evidence_missing_in_m10`
- `raw_m4_index_still_internal_not_m7`
- `public_same_stream_wording_review_missing`
- `system_python_binding_gap_open`
- `m7_row_level_release_review_missing`

## Goal-Level Decision Audit

Decision: interpret M10 accounting warning as an independent-median methodology
note, not an event-ordering failure.

1. Did I make a foolish decision?

   No. The decision preserves the raw artifact and adds a stricter explanation
   gate instead of hiding the warning.

2. If yes, what actions made the decision foolish?

   It would be foolish to edit raw evidence into a clean pass, cite M10 as
   public same-stream proof, or use the note as a `true_zero_copy` claim.

3. Was there another path?

   Yes. I could leave the warning as an unexplained release blocker. That would
   keep confusing users and reviewers even though the per-sample event checks
   are clean.

4. Can I now try a different path that truly solves the problem?

   Yes. Keep raw M4 classification intact, add this audited interpretation
   packet, record the external-review closure, and keep public same-stream/M7
   closure blocked until transfer-counter, system-Python, wording, and row-level
   release evidence exist.
