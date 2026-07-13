# Call For Review - Goal5354 X-HD Radius-Growth Schedule Semantics

## Scope

Please strictly review Goal5354:

```text
history/internal_docs/goal5354_xhd_radius_growth_schedule_semantics_result_2026-07-09.md
src/rtdsl/radius_schedule.py
src/rtdsl/__init__.py
tests/goal5354_radius_growth_schedule_test.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5354_radius_growth_semantics.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5354_radius_growth_semantics.json
```

Goal5354 starts the semantic mapping of the author RT `tune_radius` family, but
does **not** wire `tune_radius` into the X-HD RTDL route. It extracts a generic
radius-growth schedule helper into RTDL core and records the author source rule
as the reference for this first semantic substrate.

## Expected Verdict Labels

Use one of:

```text
approve_goal5354_radius_growth_schedule_semantics
approve_with_required_amendments
block_goal5354_radius_growth_schedule_semantics
```

## Review Questions

1. Does `src/rtdsl/radius_schedule.py` correctly implement the pinned author
   source semantics recorded from `src/hd_impl/hausdorff_distance_rt.h`
   lines 398-419, especially the adaptive strict less-than rule:
   `reduced_factor < 1 / expand_factor`?
2. Do the tests cover the important edge cases: adaptive low reduction,
   exact `1/8` boundary falling to `+4 * cell_diagonal`, double/add modes,
   clamp to upper bound, no unresolved items, already-at-upper-bound, and
   fail-closed invalid inputs?
3. Is the RTDL core API app-neutral? In particular, do the exported core names
   avoid `xhd`, `paper`, `author`, and figure-specific semantics?
4. Is the non-X-HD retry-radius consumer in the tests sufficient evidence that
   the helper is a generic bounded-search schedule helper rather than an X-HD
   primitive?
5. Does the artifact correctly state the current X-HD mapping boundary:
   `helper_semantics_available=true`, `route_uses_helper=false`, and explicit
   `run_xhd_rtdl_hd_exec` `-tune_radius` remains fail-closed?
6. Does the report avoid claiming author RT-core algorithm equivalence,
   author `tune_radius` route mapping, Figure 8 reproduction, performance
   improvement, or full X-HD paper reproduction?
7. Is it correct that no POD evidence is required for this goal because the
   work is a local source-semantics/API extraction, while the next behavior
   mapping goal may require POD author/RTDL trace comparison?
8. Should the next goal be `wire_tune_radius_to_cell_mbr_route_under_explicit_flag`
   only after a trace-comparison plan exists, or is there a stronger immediate
   prerequisite?

## Expected Answer Shape

Please answer in this structure:

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
8. ...
```

## Claim Boundary To Enforce

Allowed:

```text
RTDL has a generic radius-growth schedule helper.
The helper matches the pinned author add/double/adaptive update rule in isolation.
The X-HD app can use this helper in a future trace-mapping goal.
```

Not allowed:

```text
author RT-core algorithm equivalence
author tune_radius route mapping
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
silent acceptance of explicit author -tune_radius flags
```
