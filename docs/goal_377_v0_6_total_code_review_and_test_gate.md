# Goal 377: v0.6 total code review and test gate

## Why this goal exists

The `v0.6` line now has enough code and enough bounded Linux evidence that the
final pre-release risk is no longer "missing implementation." It is whether the
full `v0.6` code surface has been reviewed and tested as one coherent line.

## Scope

In scope:

- total code review of the `v0.6` graph code surface
- total review of the focused `v0.6` graph tests and their coverage value
- execution of the main focused `v0.6` graph test gate
- explicit findings on bugs, weak tests, stale code, and missing regression coverage

Out of scope:

- new workload design
- new backend implementation
- release tagging

## Required review targets

At minimum, this gate should cover:

- `src/rtdsl/graph_reference.py`
- `src/rtdsl/graph_datasets.py`
- `src/rtdsl/graph_eval.py`
- `src/rtdsl/external_baselines.py`
- `src/rtdsl/oracle_runtime.py`
- `src/native/oracle/rtdl_oracle_graph.cpp`
- the `goal345` through current `goal37x` graph tests
- the current graph scripts used for Linux evaluation

## Exit condition

This goal is complete when the repo has:

- a saved total code-review/test report
- at least one external review
- a saved Codex consensus note
- an honest verdict on whether the `v0.6` code surface is release-clean enough
