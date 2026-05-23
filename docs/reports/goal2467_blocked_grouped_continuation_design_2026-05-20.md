# Goal2467 - Generic blocked grouped-continuation design

Date: 2026-05-20

Status: Mac-local design and static contract work only. Pod validation is not
available, so this report does not authorize native implementation closure,
performance claims, or release wording.

## Purpose

Goal2461, Goal2463, and Goal2465 removed the obvious grouped-stream overheads:

- self-query grouped union no longer repacks/uploads query points from host;
- dense all-items rows can run without predicate or fallback workspaces;
- all-items `target <= source` hits are culled before anyhit.

The remaining hard target is now the generic grouped-union pass itself. The
current native path performs monotonic parent updates directly from RT hits, so
dense rows are still exposed to high global atomic pressure.

Goal2467 defines the next primitive as:

```text
generic_fixed_radius_blocked_grouped_component_continuation_3d
```

This is a fixed-radius hit-stream continuation design, not a DBSCAN primitive.

## Proposed Contract

Input:

- prepared fixed-radius 3-D search structure;
- radius;
- optional predicate flags for mixed-predicate grouped union;
- optional all-items mode when every item satisfies the predicate;
- parent workspace;
- segment/block sizing policy.

Output:

- component parent or component label workspace;
- optional fallback candidate workspace for predicate-false items;
- metadata describing segment count, policy, predicate mode, transfer mode, and
  whether the result used RT cores.

Native vocabulary must stay generic:

- use `fixed_radius`, `hit_stream`, `grouped_union`, `component`, `segment`,
  `block`, `predicate`, `parent`, `label`;
- do not use `dbscan`, `cluster`, `min_neighbors`, or app names in native ABI or
  native metadata.

## Design Direction

The next prototype should reduce global atomic pressure by staging hit handling
before global parent convergence. Candidate implementation routes:

1. Query-block staging: each launch or logical block processes a bounded query
   range, writes local parent updates, then merges into the global parent
   workspace.
2. Cell/block staging: partition prepared search items by spatial cell or Morton
   bucket, process nearby cell-pair blocks, then merge block-local unions.
3. Segmented hit-stream reduction: convert RT hit traffic into bounded
   per-segment union proposals, reduce duplicate or redundant proposals, then
   apply global parent updates in a second phase.

The first implementation should prefer the least invasive route that can be
tested on Mac with static contracts and on pod with the existing RTX A5000
benchmark packet.

## Required Telemetry

The blocked/segmented prototype must report enough telemetry to explain whether
it actually attacks global atomic pressure:

- `segment_count`;
- `segment_target_hits`;
- `max_segment_hits`;
- `global_parent_atomic_attempts`;
- `global_parent_atomic_successes`;
- `local_or_segment_union_proposals`;
- `deduplicated_union_proposals`;
- `proposal_rejection_rate`;
- `fallback_to_unblocked_grouped_union`.

For Route 3, `proposal_rejection_rate` is defined as:

```text
1 - deduplicated_union_proposals / max(1, local_or_segment_union_proposals)
```

This lets the pod packet compare whether segmented proposal reduction removes
enough redundant global updates to justify extra launches or local buffering.

## Memory-Bound Policy

The first prototype must be fail-closed and fixed-budget:

- segment buffers have an explicit capacity derived from `segment_target_hits`;
- overflow must set `fallback_to_unblocked_grouped_union = true` or return a
  typed capacity error;
- the native path must not silently grow unbounded temporary buffers;
- the benchmark app must report the configured segment capacity and any
  fallback/capacity event in metadata.

Dynamic growth can be studied later, but it would hide the memory-pressure
signal that this goal is trying to measure.

## Planner Surface Added

The benchmark app now exposes a design-only planner:

```python
plan_rt_dbscan_blocked_grouped_continuation_design(...)
```

It intentionally returns:

```text
runtime_executable = False
design_status = needs-more-evidence
selected_mode = design_only_generic_blocked_grouped_stream_candidate
target_primitive = generic_fixed_radius_blocked_grouped_component_continuation_3d
```

This records the sizing estimate and contract boundary without becoming a
hidden dispatcher.

## Mac-Local Reference Simulator

While the pod is unavailable, the benchmark app also exposes a CPU-only oracle:

```python
simulate_fixed_radius_blocked_grouped_component_continuation_3d(...)
```

This simulator is not a native route and not a performance proxy. Its job is to
fix the semantic and telemetry contract before GPU implementation:

- it generates generic fixed-radius hit-stream pairs;
- it applies predicate-true grouped union semantics;
- it partitions hits into fixed-size segments;
- it deduplicates segment-local union proposals;
- it builds non-fallback component labels from the simulated segmented parent
  workspace, not from a separate all-pairs shortcut;
- it records the telemetry required for the future pod packet;
- it falls back closed when a segment exceeds the configured fixed capacity.

The simulator is intentionally marked with:

```text
reference_only = true
native_abi_added = false
runtime_route_authorized = false
performance_claim_authorized = false
```

Focused Mac tests compare its labels against the existing CPU spatial-bucket
reference and validate overflow/fallback telemetry.

Reference-only local sample, `clustered3d`, 96 points, radius `0.055`,
`segment_target_hits = 64`:

```text
hit_stream_pair_count = 562
predicate_true_count = 60
segment_count = 9
max_segment_hits = 64
baseline_global_parent_atomic_attempts = 382
global_parent_atomic_attempts = 289
global_parent_atomic_successes = 56
deduplicated_union_proposals = 289
proposal_rejection_rate = 0.24345549738219896
fallback_to_unblocked_grouped_union = false
```

This is not performance evidence. It is a small semantic/telemetry fixture that
the future native path should match in field meaning.

## Claim Boundary

- No native ABI was added.
- No runtime route was changed.
- No GPU timing was collected.
- No performance claim is authorized.
- This design is app-independent at the engine boundary; RT-DBSCAN remains only
  the benchmark app used to stress the generic primitive.
- Pod validation and external review are required before this can close as an
  implementation goal.

## Next Pod Packet When Available

When a pod is available again:

1. Build current `origin/main` with OptiX.
2. Re-run the Goal2465 baseline packet to confirm the current tail medians.
3. Implement one blocked/segmented prototype behind a new generic metadata path.
   The native prototype should match the Mac-local reference simulator's
   semantic output and telemetry field names.
4. Compare against Goal2465 on at least:
   - `clustered3d`, 32,768 points;
   - `clustered3d`, 65,536 points.
5. Report native grouped-union time, total grouped-stream time, predicate mode,
   segment count, fixed segment capacity, overflow/fallback status,
   atomic-attempt telemetry, proposal-rejection telemetry, and exact
   correctness.

Until that evidence exists, Goal2467 is a reviewed design candidate, not a
claimed optimization.
