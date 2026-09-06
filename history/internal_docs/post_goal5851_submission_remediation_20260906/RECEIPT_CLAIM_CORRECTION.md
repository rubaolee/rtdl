# Additive correction to the pre-adjudication self-review

Date: 2026-09-06

Status: `CORRECTION_RECORDED__HISTORICAL_REPORT_PRESERVED`

The historical file
`history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md`
states at lines 627-628:

> The evidence workers do materialize and bind those receipts after timing.

That sentence is inaccurate if `those receipts` means the receipt created for
every timed execution. The worker validates every returned output against the
frozen oracle after its timer, but it does not expand, validate, bind, or retain
the 27-field operation receipt for each timed call. After the timing loop it
performs one additional `include_diagnostics=True` execution and retains that
separate diagnostic traversal receipt.

Correct replacement fact:

> The formal worker validates every timed result against the frozen output
> contract after timing. It does not materialize or retain a complete physical
> operation receipt for every timed call; it runs and retains one separate
> diagnostic execution after the timing loop.

Evidence:

- `experiments/goal5848_strong_baseline/worker.py:168-186,268-273,476-502`;
- `src/rtdsl/v4_rtdlexe.py:5308-5487,6254-6295`;
- `experiments/goal5848_strong_baseline/contracts.py:627-653`;
- all 32 final A workers have 128 steady samples, `latest_output_sha256=null`,
  one `diagnostic_traversal_receipt`, and one worker-level output digest.

The original self-review remains unchanged for custody. This additive record
does not alter raw evidence, authority status, or the finding that no wrong
output was observed in the successful GPU transactions.
