# Call For Review: Goal5007 P3 Fresh Fast-Pack Optimization

Please review:

```text
history/internal_docs/goal5007_p3_fresh_fastpack_optimization_result_2026-07-05.md
history/internal_docs/goal5007_p3_fresh_fastpack_probe.py
history/internal_docs/goal5007_p3_fresh_optimization_artifacts_2026-07-05/summary.json
```

## Requested Verdict Label

```text
approve_goal5007_p3a_lsi_prewarm_win_p3b_sort_backend_blocked
```

## Review Questions

1. Is Goal5007 using the correct fixed regime: top4 County x Zipcode, warm
   long-lived process, fresh overlay, writer-free fast-pack route, no
   device-resident carrier?
2. Does the P3-A evidence support a real route-window improvement from generic
   LSI prewarm: `4.297s -> 3.317s`, with the improvement landing in the LSI
   phase (`2.708s -> 1.733s`)?
3. Does the report correctly keep the prewarm time (`~1.246s`) separate and
   avoid presenting this as a cold CLI one-shot speedup?
4. Is the prewarm generic rather than RayJoin-specific, given that it uses the
   public `prepare_planar_map_lsi_2d_optix` route on a synthetic one-segment
   input?
5. Is it correct that this is a useful `~1.30x` warm-process fresh improvement,
   not a 10x result and not a true query-many measurement?
6. Does the P3-B decision correctly reject immediate sort replacement in the
   current POD, given that CuPy/CUB/Thrust/PyCUDA are unavailable and Goal4995
   already showed CPU lexsort is much slower?
7. Is it correct to require a future generic RTDL ordering primitive or supported
   runtime backend before replacing the current in-app Numba bitonic sort?
8. Does Goal5007 preserve the generic-system boundary and avoid adding a
   RayJoin-specific core sorter, workspace shortcut, or hidden app kernel?
9. Should Goal5007 close with:

```text
completed_p3a_generic_lsi_prewarm_fresh_win__p3b_generic_sort_backend_blocked
```
