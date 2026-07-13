# Goal5280 - Heavy-Offload Non-XHD Consumer Gate Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5280 strengthens the genericity evidence for the Goal5279 heavy/offload
worklist API.  It adds a separate non-X-HD consumer gate using a retry/backlog
scheduling scenario rather than a spatial or paper-reproduction workload.

## Why This Goal Exists

Goal5279 already introduced the generic worklist reference helper:

```text
heavy_offload_worklist_numpy_columns
```

But the Figure 11 path is high risk: a generic-looking queue could easily become
an X-HD-shaped workaround.  Goal5280 adds a behavior-level consumer outside the
X-HD / Hausdorff domain before moving to native telemetry.

## Consumer Scenario

The consumer models a generic retry scheduler:

```text
source id       = scheduler worker / job source
primitive id    = retry shard / backlog region
work_count      = backlog size
miss_mask       = failed shard needing retry
deferred_mask   = explicitly deferred shard
heavy_threshold = backlog threshold for heavy processing
```

This is not a geometry, Hausdorff, paper, or X-HD workload.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5280_heavy_offload_non_xhd_consumer_gate_2026-07-09.json
```

Main result:

```text
input rows: 5
selected rows: 4
work_source_ids:    [201, 202, 203, 204]
work_primitive_ids: [11, 12, 13, 14]
work_kind_codes:    [3, 1, 2, 1]
                    [deferred, active, miss, active]
heavy_offload_peak_rows: 4
heavy_offload_queue_peak_bytes: 64
```

Overflow control:

```text
row_capacity: 3
attempted_row_count: 4
overflowed: true
row_count: 0
partial_rows_emitted: false
```

## Validation

```text
py -m unittest \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test \
  tests.goal5279_generic_heavy_offload_worklist_test

Ran 8 tests in 3.754s
OK
```

The tests verify:

- active, miss, and deferred rows all appear in one non-X-HD consumer;
- telemetry records queue capacity / queue bytes / peak rows;
- overflow remains fail-closed;
- the consumer and helper source do not contain X-HD / Hausdorff / paper app
  identity tokens.

## Claim Boundary

This goal does not prove:

- X-HD Figure 11 reproduction;
- author memory parity;
- native backend completion;
- native/POD peak queue telemetry;
- performance improvement;
- full paper reproduction.

It proves only that the Goal5279 helper is usable by an independent non-X-HD
consumer and therefore should not be read as a paper-app-only workaround.

## Next Step

The next substantive goal is Goal5281:

```text
native/POD telemetry ABI spike
```

Goal5281 should make the queue peak evidence real on the native side rather
than only a NumPy/CPU reference calculation.
