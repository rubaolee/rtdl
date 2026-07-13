# Goal5007: P3 Fresh Fast-Pack Optimization Result

Date: 2026-07-05

## Verdict

`completed_p3a_generic_lsi_prewarm_fresh_win__p3b_generic_sort_backend_blocked`

This goal executes the safe P3 work authorized by the owner directive:

1. P3-A: measure whether generic LSI compile/prewarm can reduce the current
   fast-pack writer-free binary route window.
2. P3-B: check whether the current POD has a better generic GPU ordering
   backend than the in-app Numba bitonic sort.

The fixed product measurement target for this goal is:

```text
top4 County x Zipcode / warm long-lived process / fresh overlay /
writer-free binary route / fast-pack route / no device-resident carrier
```

This is not a cold CLI one-shot measurement, not prepared replay, and not true
query-many.

## Artifacts

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Local artifacts:

```text
history/internal_docs/goal5007_p3_fresh_fastpack_probe.py
history/internal_docs/goal5007_p3_fresh_optimization_artifacts_2026-07-05/
```

Key artifact:

```text
history/internal_docs/goal5007_p3_fresh_optimization_artifacts_2026-07-05/summary.json
```

## P3-A: Generic LSI Prewarm On The Fast-Pack Route

The probe runs the current headline fast-pack route:

```text
--device-columnar
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
--compiled-group
```

It explicitly does **not** use:

```text
--device-resident-carrier
--prepared-operator-session
--repeat
```

The prewarm uses the public generic LSI API on a one-segment synthetic input:

```text
prepare_planar_map_lsi_2d_optix(...)
run_bounded_pair_id_device_columns(...)
```

No RayJoin-specific core path is added.

### Result

Three baseline runs and three prewarmed runs were measured in separate route
windows.

| Route | Median writer-free route window | Median LSI phase | Median downstream floor | Median prewarm time |
|---|---:|---:|---:|---:|
| baseline fast-pack | `4.297s` | `2.708s` | `1.620s` | n/a |
| generic LSI prewarm + fast-pack | `3.317s` | `1.733s` | `1.586s` | `1.246s` |

Delta:

```text
writer-free route window: 4.297s -> 3.317s = 0.980s improvement
LSI phase:                2.708s -> 1.733s = 0.975s improvement
```

This confirms that the reusable compile / pipeline setup part of the LSI
producer is removable from the **route window** in a long-lived process, and the
effect lands exactly where expected: the LSI phase.

### Claim Boundary

Authorized:

- generic LSI prewarm can reduce the fast-pack warm-process route window by
  about `~0.98s` on this top4 input;
- this is a real fresh-route improvement for a long-lived process model where
  the prewarm is a service/process initialization step;
- the prewarm cost is reported separately.

Not authorized:

- no cold CLI one-shot speedup if prewarm time is counted inside the same
  command;
- no 10x claim;
- no true query-many claim;
- no author-performance parity claim.

If the prewarm time itself is charged to a single one-shot command, the result is
not a win:

```text
prewarm 1.246s + route 3.317s = 4.563s
```

That is slower than the baseline route window.  Therefore this is a
long-lived-process / initialization feature, not a CLI one-shot trick.

## P3-B: Generic Sort Backend Gate

P3-B asked whether the current bitonic device sort could be replaced now by a
better generic GPU ordering primitive.

The answer in the current POD is no.

### Current POD Availability

The current POD has:

```text
numba 0.66.0
numba.cuda available: true
```

It does not have:

```text
cupy
cuda Python package
pycuda
rmm
cudf
thrust Python binding
cub Python binding
```

### Prior Sort Probe

Goal4995 already tested the cheap available alternative:

```text
CPU / NumPy lexsort backend
```

Result:

```text
device bitonic prepared route: ~0.3665s prior best
CPU lexsort route:             ~3.4125s median
```

CPU lexsort was correctly rejected.

### Decision

`generic_gpu_sort_backend_not_available_in_current_runtime`

Do not implement a RayJoin-specific sorter inside the app to make this look
solved.  A real replacement needs a generic RTDL ordering facility, such as:

- native CUB/Thrust-backed segmented lexicographic sort;
- or a supported CuPy/CUDA sorting backend in the runtime image;
- or a generic RTDL columnar ordering primitive with non-RayJoin consumers.

Until then, the in-app Numba bitonic sort remains the available generic-ish
route for this app, and the sort replacement is blocked rather than noised into
the codebase.

## Performance State After Goal5007

The honest current numbers are:

| Regime / route | Writer-free time | Status |
|---|---:|---|
| fast-pack baseline, warm-process fresh | `~4.30s` median in this POD sample | product-relevant route window |
| fast-pack with generic LSI prewarm | `~3.32s` median route window | valid long-lived-process route window; prewarm separate |
| prewarm + route charged as one CLI command | `~4.56s` | not a one-shot win |
| prepared operator body, same input | `~0.331s` | diagnostic; not true query-many |

The 10x target remains gated.  Goal5007 improves the honest warm-process fresh
route by about `1.30x`:

```text
4.297 / 3.317 ~= 1.30x
```

This is useful progress, not the 10x result.

## What Remains

1. P2 still must demonstrate a real prepared-base / same-domain / distinct-query
   workload before any `query-many` claim.
2. The generic sort replacement remains blocked until RTDL has a real generic
   GPU ordering primitive or the runtime image includes a supported backend.
3. Distinct-domain fresh still has the `~1.7s` workspace floor identified in
   Goal5003.
4. Device-resident carrier remains stopped for v2.14.3 unless it passes the
   payoff gate in a measured target regime.

## Exit Label

`completed_p3a_generic_lsi_prewarm_fresh_win__p3b_generic_sort_backend_blocked`
