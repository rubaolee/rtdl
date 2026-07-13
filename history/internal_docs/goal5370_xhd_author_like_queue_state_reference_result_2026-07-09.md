# Goal5370 - X-HD Author-Like Queue-State Reference

Date: 2026-07-09

Status: `implemented_review_pending`

## Verdict Label

```text
bounded_author_like_queue_state_reference_ready
```

Exit label:

```text
bounded_queue_state_reference_matches_author_rows__dragon_lb_still_unimplemented
```

## Purpose

Goal5369 established that explicit `-lb` denominator parity requires more than
a scalar radius or raw kind2 count.  It needs queue/current-best state.

Goal5370 builds the smallest concrete queue-state representation in the X-HD
app layer:

```text
active_source_ids
active_in_queue_indices
nearest_target_ids
nearest_distances
current_best_sq
confirmed_source_ids
unresolved_source_ids
cmax2_before
cmax2_after
```

This is a reference shape for the next Dragon -> AsianDragon `-lb` gate.  It is
not explicit `-lb` support and not a large-input denominator comparison.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5370_author_like_queue_state_reference.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5370_author_like_queue_state_reference.json
tests/goal5370_author_like_queue_state_reference_test.py
```

## Input

Bounded existing fixture:

```text
bounded3d_a.wkt -> bounded3d_b.wkt
author artifact = bounded3d_author_hd_exec_output_pod.json
```

Author row:

```text
Iteration      = 1
Radius         = 2.0
NumInputPoints = 9
NumOutputPoints = 0
CMax2          = 4.0
OffloadingSize = 0
```

## Result

RTDL queue-state reference matches the author row:

```text
matched = true
mismatch_count = 0
```

The emitted state includes:

```text
active_source_ids = [0,1,2,3,4,5,6,7,8]
active_in_queue_indices = [0,1,2,3,4,5,6,7,8]
confirmed_source_ids = [0,1,2,3,4,5,6,7,8]
unresolved_source_ids = []
nearest_distances = [0.1,0,0,0,0,0,0,0,2.0]
current_best_sq = [0.01,0,0,0,0,0,0,0,4.0]
```

Because this bounded fixture is terminal in one iteration, it proves the state
representation and row comparison, not nonterminal `-lb` offload behavior.
Goal5361 remains the nonterminal queue-row evidence; Goal5370 adds the missing
state-vector shape.

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5370_author_like_queue_state_reference.py
py -m py_compile Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5370_author_like_queue_state_reference.py
py -m unittest tests.goal5370_author_like_queue_state_reference_test tests.goal5369_lb_queue_state_requirements_test
```

Result:

```text
Ran 5 tests OK
```

Known local environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
Goal5370 defines and validates a bounded app-owned queue-state reference shape
that can carry active source ids, in-queue indices, current-best/cmin2, and
confirmed/unresolved source sets.
```

Not authorized:

```text
explicit -lb support
Dragon -> AsianDragon lb denominator parity
row-count parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
performance claim
full X-HD paper reproduction
```

## Next Work

The next gate can now reuse this state shape on the large Dragon -> AsianDragon
case:

```text
1. Execute/reconstruct the author-like queue through the relevant iteration.
2. Preserve active source ids and in-queue indices.
3. Carry per-source current_best_sq / cmin2.
4. Run count-only raw offload telemetry under that active queue and current
   best state.
5. Compare against author OffloadingSize = 27,133,990 and author-width bytes.
```
