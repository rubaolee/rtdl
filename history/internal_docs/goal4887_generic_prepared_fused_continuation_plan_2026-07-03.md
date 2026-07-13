# Goal4887: Generic Prepared Session + Fused Continuation Plan

Date: 2026-07-03

Status: `proposed_for_external_review__do_not_implement_before_approval`

## One-Line Goal

Turn the RayJoin Section 5.7 performance lesson into **generic RTDL engine
work**: prepared planar-map sessions, stable row-buffer contracts, and formal
Numba partner continuation, without adding RayJoin-specific runtime shortcuts.

## Why This Goal Exists

The current RayJoin reproduction line proved correctness and exposed the next
real systems problem.

Current evidence on the Australia representative Section 5.7 workload:

| View | AuthorPatch C++/CUDA/OptiX | RTDL+Python | RTDL+Python+Numba v2 | Meaning |
| --- | ---: | ---: | ---: | --- |
| One-shot end-to-end | `148.939 s` logged phase sum | `117.258 s` | `103.786 s` | RTDL+Numba is faster in this cold one-shot view. |
| Query + output, excluding read/build | `0.844 s` | `36.076 s` | `20.920 s` | AuthorPatch is `24.78x` faster than RTDL+Numba. |
| Core query compute, excluding read/build and output write | `0.0421 s` | `19.550 s` | `18.880 s` | AuthorPatch is `448.47x` faster than RTDL+Numba. |

The lesson is sharp:

- RTDL can now express the reproduction using public primitives plus Python and
  Numba continuation.
- Numba already removed a real Python writer bottleneck:

  ```text
  output-chain write: 16.525 s -> 2.040 s
  writer-phase speedup: 8.10x
  ```

- But the RTDL hot path is still far behind the author's fused native route.
- The next work must therefore target the generic execution structure, not the
  RayJoin app surface.

## V3/V4 Lessons To Reuse

V3/V4 are sealed as experimental work and are not release surfaces. However,
they produced useful lessons for this goal.

Useful lessons:

1. **Prepared/execution-graph intent was correct.**
   V3's execution-graph/residency idea targeted the same problem: primitive
   boundaries returning to Python and repeatedly materializing rows. The error
   was that it never became a productized trunk.

2. **Partner continuation is the right abstraction.**
   V3/V4 repeatedly showed that RTDL should own RT traversal and let explicit
   partners such as Numba or CuPy own non-RT continuation work. Goal4886
   confirmed this with a bounded Numba writer win.

3. **Operator/fusion must stay app-agnostic.**
   V4 clarified the rule that the engine may contain generic operators and
   continuation primitives, but must not contain app identity such as
   "RayJoin kernel" or hidden app-specific fast paths.

4. **Phase accounting is mandatory.**
   End-to-end, prepared hot path, primitive phase, output phase, and partner
   phase must be reported separately. A single total hides the truth.

What must not be reused:

- V3/V4 release wording;
- V4 wrapper-only APIs without engine changes;
- app-specific helper calls disguised as generic language features;
- C ABI / embedding / unrelated future-host work.

## Generic Route Only

Goal4887 is allowed to improve RTDL's generic planar-map and continuation
engine. It is not allowed to make RayJoin special.

Allowed generic work:

- prepared planar-map sessions;
- reusable CDB/map adapter feeding generic prepared maps;
- stable LSI row buffers;
- stable point-location/PIP row buffers;
- standard continuation buffers;
- Numba partner continuation API;
- generic row operations:
  - map rows;
  - filter rows;
  - compact rows;
  - group rows;
  - reduce rows;
  - skip-mask generation;
- phase accounting and materialization accounting.

Forbidden RayJoin-specific work:

- adding `rayjoin_*` public APIs;
- importing private `rtdsl.rayjoin_overlay` from the new route;
- adding hidden native fast paths keyed on RayJoin data or Section 5.7;
- moving output-chain format rules into RTDL core;
- treating `AuthorOfficial` comparator logic as a language feature;
- claiming any speedup beyond measured, bounded evidence.

## Current Generic Baseline

Current public generic support:

1. `planar-map LSI`
   - expresses line/segment intersection rows;
   - used for Section 5.2.

2. `directed point-location / PIP`
   - expresses directed point-in-planar-map classification;
   - used for Section 5.3.

3. app-layer Python composition
   - currently assembles Section 5.7;
   - mostly outside the generic engine.

4. Numba app-layer helper
   - currently accelerates writer skip decisions;
   - not yet a formal RTDL partner continuation API.

## Desired Generic Support After Goal4887

Goal4887 should produce these generic engine capabilities:

1. **Prepared planar-map session**

   The engine should let users prepare maps once and reuse packed data, BVH,
   scale metadata, and stable buffers across repeated queries.

   Sketch:

   ```python
   left = rtdl.planar_map.from_cdb("left.cdb")
   right = rtdl.planar_map.from_cdb("right.cdb")

   with rtdl.prepare_planar_map_session(left, right) as session:
       ...
   ```

2. **Stable row-buffer contracts**

   LSI and PIP outputs should be stable buffers with explicit schema, not
   ad-hoc Python structures.

   Example schemas:

   ```text
   LSIRows:
     left_edge_id
     right_edge_id
     intersection_x_num
     intersection_y_num
     flags

   PointLocationRows:
     point_id
     face_id
     closest_edge_id
     classification
     flags
   ```

3. **Formal Numba partner continuation**

   Users should be able to attach a Numba continuation to RTDL-managed row
   buffers without monkeypatching app helper functions.

   Sketch:

   ```python
   rows = session.lsi().query()
   faces = session.point_location(points).query()

   out = session.continue_with_numba(
       inputs=[rows, faces],
       kernel=user_kernel,
       output_schema="custom_rows",
   )
   ```

4. **Prepared pipeline / execution graph**

   The engine should know the stage graph so it can account for, and eventually
   reduce, Python and host materialization boundaries.

   Sketch:

   ```python
   result = (
       session.pipeline()
       .lsi()
       .midpoints()
       .point_location()
       .continue_with_numba(user_overlay_like_kernel)
       .compact()
       .run()
   )
   ```

5. **Mandatory phase accounting**

   Every run should report:

   - cold load/pack time;
   - prepared query time;
   - LSI time;
   - PIP time;
   - row materialization time;
   - partner continuation time;
   - output write time;
   - host/device transfer or host-materialization status.

## User-Visible Programming Difference

Current user shape:

```python
left = load_cdb("left.cdb")
right = load_cdb("right.cdb")

with rtdl.prepare_planar_map_lsi_2d(left) as lsi:
    lsi_rows = lsi.query(right)

midpoints = python_make_midpoints(lsi_rows)

with rtdl.prepare_directed_point_location_2d(right) as pip:
    pip_rows = pip.query(midpoints)

out = python_assemble_output(lsi_rows, pip_rows)
```

Goal4887 target shape:

```python
left = rtdl.planar_map.from_cdb("left.cdb")
right = rtdl.planar_map.from_cdb("right.cdb")

with rtdl.prepare_planar_map_session(left, right) as session:
    out = (
        session.pipeline()
        .lsi()
        .midpoints()
        .point_location()
        .continue_with_numba(user_continuation_kernel)
        .compact()
        .run()
    )
```

This is not meant to be only a wrapper. If the implementation still returns to
Python between every stage and only hides that behind fluent syntax, the goal
fails.

## Architecture Work Required

### A. Prepared map/session foundation

Tasks:

- define prepared planar-map session object;
- preserve packed vertices/edges/chains and scale metadata;
- preserve RT/native prepared state when safe;
- expose cold vs prepared phase timing;
- make repeated query use explicit and testable.

Exit gate:

- repeated query over same maps does not re-run CDB parse/load-pack;
- summary proves cold and prepared phases are separated.

### B. Row-buffer ABI

Tasks:

- define `LSIRows` and `PointLocationRows`;
- provide Python accessors plus low-level contiguous arrays;
- record dtype, shape, ownership, lifetime, and materialization status;
- preserve correctness parity with existing public LSI/PIP results.

Exit gate:

- current Section 5.2/5.3 outputs can be regenerated from the row-buffer path;
- row-buffer path is not RayJoin-specific.

### C. Formal Numba partner continuation

Tasks:

- define Numba kernel signature;
- validate input row schemas before execution;
- provide CPU/Python reference fallback;
- record partner, kernel, phase time, and byte/parity result;
- forbid hidden automatic partner selection.

Exit gate:

- Goal4886 writer-skip logic can be expressed through the formal partner API,
  not by monkeypatching a harness.

### D. Pipeline execution graph

Tasks:

- define a small prepared pipeline graph for planar-map workloads;
- support LSI -> midpoint generation -> PIP -> partner continuation -> compact;
- record materialization boundaries;
- keep graph operators generic.

Exit gate:

- the RayJoin representative route can run through the generic graph without
  calling `rayjoin_overlay`.

### E. Performance regression and claim boundary

Tasks:

- rerun the Australia representative workload;
- compare:
  - current RTDL public primitive route;
  - RTDL+Numba Goal4886 route;
  - Goal4887 prepared/fused route;
  - AuthorPatch logged phases, only with the same boundary caveats as Goal4886.

Exit gate:

- no correctness regression;
- no broad RayJoin claim unless data supports it;
- phase table separates cold, prepared, query, output, and partner time.

## Expected Performance Targets

These are engineering targets, not promises.

Baseline:

```text
Current RTDL+Numba v2 one-shot end-to-end: 103.786 s
Current RTDL+Numba v2 query+output:         20.920 s
Current RTDL+Numba v2 core query compute:   18.880 s
AuthorPatch query+output:                    0.844 s
AuthorPatch core query compute:              0.0421 s
```

### Target 1: cold one-shot

Target:

```text
75-95 s
```

Reason:

- load/pack is currently about `77.051 s`;
- if cold run still needs text CDB parse, it may remain large;
- some overhead should reduce through prepared structure reuse inside the run,
  but cold one-shot is not the main success criterion.

### Target 2: prepared hot run

Target:

```text
3-8 s query+output
```

Reason:

- prepared/cache removes repeated load/pack;
- formal Numba continuation should keep the writer cost near the Goal4886
  `~2 s` range or below;
- fused continuation should reduce Python/host boundaries in the remaining
  `~18.9 s` core path.

### Target 3: stretch goal

Stretch:

```text
<= 1.5 s prepared query+output
```

Reason:

- this would begin to approach the author's fused native query+output shape;
- it likely requires deeper native/fused continuation than Goal4887 can safely
  promise.

### Non-goal

Goal4887 does not promise to beat:

```text
AuthorPatch core query compute: 0.0421 s
```

That would require a much deeper fused native overlay kernel. Goal4887 should
make progress toward that shape, not pretend it is already there.

## Acceptance Criteria

Goal4887 may be considered successful if all are true:

1. no RayJoin-specific runtime API or hidden helper is introduced;
2. prepared session avoids repeated load/pack in prepared runs;
3. LSI/PIP row-buffer schemas are explicit and reusable;
4. Numba continuation is called through a formal partner API;
5. RayJoin representative output remains byte-equal to the established
   comparator;
6. prepared hot query+output improves materially over `20.920 s`;
7. phase accounting clearly shows where the time moved;
8. all claims remain bounded.

Preferred performance success:

```text
prepared hot query+output <= 8 s
```

Strong performance success:

```text
prepared hot query+output <= 3 s
```

Failure labels:

- `blocked_by_row_buffer_contract_gap`
- `blocked_by_prepared_session_lifetime_gap`
- `blocked_by_partner_api_gap`
- `correct_but_not_faster_than_goal4886`
- `rejected_as_rayjoin_specific_shortcut`

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid path would be to make another pretty wrapper while the engine
   still bounces through Python after every primitive.

2. **What actions would make this stupid?**

   - adding a `rayjoin_overlay_fast()` path;
   - hiding private helpers behind generic names;
   - reporting only end-to-end cold time;
   - claiming Numba accelerated LSI/PIP;
   - skipping row-buffer/lifetime design.

3. **Is there another path that avoids getting stuck?**

   Yes: implement the smallest generic prepared session and row-buffer contract
   first, then attach Numba continuation only after schemas are stable.

4. **Can I start a different path that truly solves the problem?**

   Yes. The path is generic engine work:

   ```text
   prepared session
   + row-buffer ABI
   + formal partner continuation
   + materialization-aware pipeline
   ```

## External Review Questions

1. Is this goal truly generic engine work, or does it still hide RayJoin
   special cases?
2. Are the expected performance targets realistic and sufficiently bounded?
3. Is the row-buffer ABI the right first architectural work, or should prepared
   session come first?
4. Does the proposed Numba partner API preserve explicit user partner choice?
5. Are the acceptance/failure labels sharp enough to prevent another V3/V4-style
   overclaim?
6. Should implementation begin, or should the design be amended first?

## Non-Authorization

This proposed goal does not authorize:

- public release wording;
- broad RayJoin speedup claims;
- full Section 5.7 eight-pair performance claims;
- app-specific native kernels;
- any new `rayjoin_*` public API;
- hiding private helpers behind fluent syntax;
- claiming AuthorPatch hot-path parity.
