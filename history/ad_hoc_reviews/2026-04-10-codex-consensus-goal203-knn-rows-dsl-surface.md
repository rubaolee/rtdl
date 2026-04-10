# Codex Consensus: Goal 203 KNN Rows DSL Surface

## Verdict

Goal 203 is the right next `v0.4` slice and the implementation is ready for
external review.

## Findings

- `rt.knn_rows(k=...)` now exists in the public API and package exports.
- lowering now produces a `knn_rows` execution plan with explicit
  `neighbor_rank` support.
- the language docs distinguish clearly between DSL/lowering support and
  runtime-not-yet-implemented status.
- the goal stays narrow and does not overclaim execution support.

## Summary

This slice gives `knn_rows` a usable authoring surface and a stable lowered plan
shape without blurring into truth-path or backend implementation work. It is a
clean follow-on to the Goal 202 contract freeze.
