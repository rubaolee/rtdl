# Goal4452 / V3.0 M56 RT-DBSCAN Route Decision Refresh

## Outcome

M56 refreshes the current RT-DBSCAN route decision after Goal4445. The current
guidance is now output contract first:

- use `output_mode="component_signature"` for cluster-size/noise/core summaries;
- use `output_mode="full"` only when the user really needs per-point Python
  cluster rows;
- keep full Python rows explicit instead of making them the default summary
  output path;
- keep prepared direct-status, partition-convergence, partition factor, and
  border-policy routes as explicit profile/policy candidates.

This is a route-guidance cleanup, not a new performance claim.

## Why This Matters

Before M56, `explain_current_benchmark_route("rt_dbscan")` still put a very long
Goal4079-Goal4177 history in `current_reader_decision`. That history remains
valid evidence, but it was the wrong first answer for app authors after Goal4445.

The new row makes the current decision readable:

1. decide whether the app needs compact summaries or full rows;
2. choose CuPy and Numba explicitly when partner aggregation matters;
3. use the older advisor/direct-status paths only when the caller explicitly
   selects that contract and accepts the measured profile/factor/policy boundary.

## Boundary

M56 does not authorize automatic partner selection, automatic output-mode
selection, a broad RT-DBSCAN speedup claim, a paper-reproduction claim, or hidden
partition-factor/border-policy tuning. It only makes the current route registry
match the already-measured Goal4445 compact-output contract.
