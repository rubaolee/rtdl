# Goal951 Two-AI Consensus

Date: 2026-04-25

Consensus status: ACCEPTED

Participants:

- Codex implementation/audit
- Euler peer review

## Agreed Scope

Goal951 moves Barnes-Hut candidate summaries into native C++ oracle
continuation. It adds:

- `RtdlFixedRadiusSummaryRow`
- `rtdl_oracle_summarize_fixed_radius_rows`
- `rt.summarize_fixed_radius_rows(rows)`

`examples/rtdl_barnes_hut_force_app.py` now uses this continuation for compact
candidate row/body/node summary fields after RTDL fixed-radius rows are
produced.

## Agreed Boundaries

Allowed:

- compact Barnes-Hut candidate summaries use native C++ continuation after
  emitted fixed-radius candidate rows are produced.
- OptiX `node_coverage_prepared` remains the bounded Barnes-Hut RT-core
  node-coverage decision path.

Not allowed:

- native Barnes-Hut opening-rule acceleration.
- native force-vector reduction acceleration.
- N-body solver acceleration.
- new RTX/public speedup claim from this goal.

## Verification

Focused Barnes-Hut/app/matrix gate:

```text
Ran 36 tests in 3.832s
OK
```

Focused matrix/source gate:

```text
Ran 9 tests in 0.001s
OK
```

Syntax and whitespace gates passed for the touched Goal951 files.

## Residual Risk

Large-count overflow behavior is not stress-tested for the `uint32_t` summary
fields. This is not a blocker for the bounded public app path, but should be
covered before claiming very large Barnes-Hut candidate-summary capacity.
