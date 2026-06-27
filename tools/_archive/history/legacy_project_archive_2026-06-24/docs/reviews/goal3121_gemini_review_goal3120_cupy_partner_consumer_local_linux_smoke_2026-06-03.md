# Goal3121: Gemini Review For Goal3120 v2.8 CuPy Partner-Consumer Local Linux Smoke

## Verdict
`accept`

## Findings by Severity

### Critical
None.

### High
None.

### Medium
None.

### Low
None.

## Claim Boundary
This smoke test provides functional evidence that the Goal3117 explicit partner-consumer front door can successfully integrate with CuPy for a specific operation (`segmented_sum_f64`) on a local Linux environment. It correctly maintains the explicit "no claims" boundary for performance, zero-copy, release authorization, hidden dispatch, or automatic partner selection, as articulated in `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY`.

### Justification for Verdict

1.  **Does Goal3120 honestly describe a functional smoke, not release/performance evidence?**
    Yes. The Goal3120 report explicitly states its status as "local Linux functional smoke, not release or performance evidence." The environment (GTX 1070) is noted as suitable for functional smoke but "not accepted release-grade performance evidence." The boundaries section consistently reiterates this, and inspection of `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` and `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py` confirms that all internal flags related to performance, release, or zero-copy claims remain `False`.

2.  **Does the smoke substantiate that explicit CuPy partner columns can execute through the Goal3117 front door for `segmented_sum_f64`?**
    Yes. The report details the successful execution of `segmented_sum_f64` using `user_selected_partner="cupy"` and caller-supplied `partner_columns` containing CuPy arrays. The result `[4.0, 10.0, 3.0]` matched the Python reference, confirming functional correctness. The underlying `v2_8_segmented_typed_stream_adapter.py` supports this by calling `partner_group_sum_by_key` when `partner="cupy"`. This aligns with the "Next Required Step" identified in the Goal3119 consensus report.

3.  **Are the claim boundaries correct?**
    Yes. The claim boundaries documented in the Goal3120 report are entirely consistent with the `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY` defined in `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` and the consensus from Goal3119. All relevant "claim flags" in the system are explicitly set to `False` and are validated to remain so by the adapter's internal logic and tests. This ensures that no unauthorized claims are implicitly made.

## Files Inspected
- `docs/reports/goal3120_v2_8_cupy_partner_consumer_local_linux_smoke_2026-06-03.md`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3119_v2_8_explicit_partner_consumer_front_door_2ai_consensus_2026-06-03.md`

## Next Step
The next logical step, as suggested by Goal3120 itself, is to proceed with a larger hardware run on a suitable CUDA host or pod. This run should:
1.  Execute more diverse partner operations through the Goal3117 front door.
2.  Compare each against the Goal3114 Python reference consumer.
3.  Measure timing separately from correctness to gather initial performance insights.
4.  Maintain the existing release/performance boundary, ensuring no claims are made until further reviewed evidence exists.
