# Goal4916 — RayJoin Performance Line Consolidation

Date: 2026-07-03

## Requested Verdict

`approve_goal4916_consolidate_current_best_and_stop_micro_optimization`

## Executive Conclusion

The current RayJoin Section 5.7 engineering line has produced a correct,
bounded, real RTDL+Numba+Python implementation route, but it has also reached
the end of useful small optimizations.

Current best verified route:

```text
public RTDL planar-map workspace
public RTDL planar-map LSI
public RTDL planar-map point-location/PIP
Numba app-layer continuation
Python exact AuthorOfficial output writer
```

Best verified prepared-hot result:

```text
Goal4915 repeat1 hot body: 3.832s
byte_equal_to_AuthorOfficial: true
```

Best productized workspace no-regression result:

```text
Goal4914 repeat1 hot body: 3.955s
byte_equal_to_AuthorOfficial: true
```

Goal4915 is slightly faster than Goal4914, but missed its hard productization
bar. Therefore, the clean product story should anchor on Goal4914 workspace API
plus the Goal4915 lesson:

```text
small app-layer writer tweaks are exhausted.
```

## What Was Actually Achieved

### Correctness

The Australia representative Section 5.7 output is byte-equal to AuthorOfficial:

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
bytes:  6189260
lines:  276320
```

### Public RTDL primitives

The route uses public, generic RTDL primitives:

- `prepare_planar_map_lsi_2d_optix`
- `prepare_planar_map_point_location_2d_optix`
- `prepare_planar_map_workspace_2d_optix`

It does not rely on `rtdsl.rayjoin_overlay` as the user-facing route.

### Numba partner role

Numba is useful, but only on the app-layer continuation/writer path:

- midpoint generation;
- point-pair dedupe;
- chain keep/skip decisions;
- writer skip-plan construction.

Numba does not replace RTDL LSI/PIP traversal and does not run inside OptiX.

### Workspace API

Goal4913/4914 turned the prepared-session experiments into a product shape:

```python
with prepare_planar_map_workspace_2d_optix(left, right, cache_dir=cache) as ws:
    rows = ws.run_lsi_pair_id_rows()
    faces0 = ws.run_left_points_in_right()
    faces1 = ws.run_right_points_in_left()
```

This is the correct user-facing lifecycle abstraction for repeated-query /
service-style planar-map workloads.

## Performance Progression

Representative Australia Section 5.7 route:

| Goal | Route | Hot Body | Writer | Correct |
|---|---|---:|---:|---|
| Goal4902 | point-location session reuse | `6.915s` | `3.031s` | yes |
| Goal4904 | prepared LSI + PIP replay | `4.638s` | `2.562s` | yes |
| Goal4910 | direct no-xsect descriptor | `3.918s` | `1.840s` | yes |
| Goal4914 | public workspace smoke | `3.955s` | `1.875s` | yes |
| Goal4915 | direct intersection flush probe | `3.832s` | `1.763s` | yes |

Interpretation:

- Prepared LSI/PIP/session reuse was the major RTDL lifecycle win.
- Numba app continuation made the writer feasible.
- Workspace API productized the route with no meaningful regression.
- Writer micro-edits now produce only small improvements.

## What Is Still Slow

The remaining hot path is not LSI/PIP traversal. In the best current runs:

- LSI replay is about `0.006s`;
- PIP traversal is tiny natively but includes Python/row conversion wrapper cost;
- output chain writer remains about `1.76s–1.88s`;
- reprojection/sorting remains about `0.88s`;
- exact text output and topology assembly dominate the remaining app layer.

Cold/setup remains real:

- workspace prepare in Goal4914/4915 is about `11–17s` depending on run noise;
- the largest setup item is prepared point-location for the larger map;
- this is an in-process workspace amortization story, not a single-run cold win.

## What We Should Stop Doing

Stop:

- point-location group-mode knob sweeps;
- no-xsect writer skip micro-edits;
- small `OutputChain` object-removal tweaks;
- pretending a `1.03x` hot-body improvement is a breakthrough;
- comparing cold/setup runs as if they are the same metric as prepared-hot runs.

These were tested and bounded.

## What Would Be Required For Another Large Win

A large next win is not likely from Python micro-edits. It would require a new,
separately reviewed architecture goal, such as:

1. **Compiled/native output writer subsystem**
   - app-output specific;
   - must be clearly separated from RTDL core primitives;
   - risks moving too much paper-app formatting into compiled code.

2. **Dataflow-to-kernel pushdown**
   - true language/runtime R&D;
   - moves user reduce/continuation logic closer to traversal;
   - this is the post-v2.14 high-performance direction, not a small patch.

3. **Cross-process prepared-structure persistence**
   - backend-specific and driver-sensitive;
   - not justified before the in-process workspace API is stabilized.

## Recommended Current State

Close this performance line as:

```text
correct bounded RayJoin Section 5.7 representative reproduction,
public RTDL workspace route validated,
Numba app-continuation acceleration validated,
small Python writer optimizations exhausted.
```

Do not claim:

- broad RayJoin speedup;
- broad RTDL speedup;
- single-run author win;
- full eight-pair Section 5.7 performance;
- raw OptiX callback support.

## Next If Continuing

If the project continues beyond this line, the next goal should not be another
micro-benchmark. It should be a new architecture decision:

```text
Do we invest in a dataflow-to-kernel pushdown compiler / in-traversal
continuation model, or do we stop at v2.14 + workspace + partner app
continuation?
```

That decision belongs to the project owner. It should not be smuggled in through
another RayJoin writer patch.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. This consolidation prevents continuing a low-yield optimization loop.

2. **What action would make this stupid?**

   Continuing to write more Python writer variants after the hard bar was
   missed twice.

3. **Was there another path?**

   Yes: jump to a native writer. That is a new architecture/product decision and
   should not be hidden inside this line.

4. **Can I start a different path that truly solves the problem?**

   Yes, but only as a new reviewed architecture goal: dataflow pushdown or a
   separate compiled output subsystem. The current v2.14 RayJoin performance
   line should now be consolidated.
