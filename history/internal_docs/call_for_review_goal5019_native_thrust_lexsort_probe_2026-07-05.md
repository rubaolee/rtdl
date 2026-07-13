# Call For Review: Goal5019 Native Thrust Lexsort Probe

Please review:

- `history/internal_docs/goal5019_native_thrust_lexsort_probe_2026-07-05.md`
- `history/internal_docs/rtdl_goal5019_bitonic_warm_top4.json`
- `history/internal_docs/rtdl_goal5019_native_thrust_top4.json`
- `history/internal_docs/rtdl_goal5019_native_thrust_warm_top4.json`

## Context

The owner challenged the earlier framing that sort was blocked by missing Python
bindings:

> Who forbade installing or using CUB/Thrust?

Goal5019 answers by implementing a native CUDA/Thrust lexsort bridge and
measuring it on the RayJoin Section 5.7 writer-free top4 route.

## Requested Review Questions

1. Does the implementation use a generic device-column lexsort contract rather
   than a RayJoin-specific native kernel?

2. Is `--native-lexsort` correctly opt-in, with the existing Numba bitonic path
   retained as the default fallback?

3. Does the POD evidence prove the native Thrust backend is available and builds
   on the current CUDA/OptiX POD?

4. Does the CPU longdouble validation evidence support correctness equivalence
   for the measured top4 route?

5. Is the performance interpretation honest: native Thrust has a small warm
   sort win (`~0.020s`) but does not move the headline route enough to be a 10x
   lever?

6. Should native Thrust lexsort remain behind `--native-lexsort` rather than
   becoming the default route?

7. Is the recommended next target correct: prepared-workspace /
   point-location-preparation costs rather than further sort work?

## Requested Verdict Label

```text
approve_goal5019_native_thrust_lexsort_correct_small_win_keep_opt_in
```
