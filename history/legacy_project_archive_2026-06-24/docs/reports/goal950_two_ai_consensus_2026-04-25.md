# Goal950 Two-AI Consensus

Date: 2026-04-25

Consensus status: ACCEPTED

Participants:

- Codex implementation/audit
- Euler peer review

## Agreed Scope

Goal950 moves the ANN candidate rerank summary into native C++ oracle
continuation. It adds:

- `RtdlKnnSummaryRow`
- `rtdl_oracle_summarize_knn_rows`
- `rt.summarize_knn_rows(rows)`

`examples/rtdl_ann_candidate_app.py` now uses this continuation for compact
row/query/rank summary fields after RTDL KNN rows are produced.

## Agreed Boundaries

Allowed:

- compact ANN rerank summaries use native C++ continuation after emitted KNN
  rows are produced.
- OptiX `candidate_threshold_prepared` remains the bounded ANN RT-core
  candidate-coverage decision path.

Not allowed:

- ANN index acceleration.
- candidate-set construction acceleration.
- KNN ranking speedup.
- recall/latency optimizer claim.
- new public RTX speedup claim from this goal.

## Verification

Focused ANN/app/matrix gate:

```text
Ran 35 tests in 1.285s
OK
```

Syntax and whitespace gates passed for the touched Goal950 files.

## Residual Risk

Large-count overflow behavior is not stress-tested for the `uint32_t` summary
fields. This is not a blocker for the bounded public app path, but should be
covered before claiming very large ANN rerank-summary capacity.
