# Goal4911 — Point-Location Prepare/Run Tradeoff Probe

Date: 2026-07-03

## Verdict Requested

`completed_prepare_tradeoff_probe__current_default_retained__no_simple_knob_win`

## Goal

After Goal4910, Antigravity recommended pivoting away from shallow writer tweaks
and toward cold/setup point-location cost. Goal4911 tests whether the remaining
point-location prepare cost is caused by a bad group/range construction default
that can be fixed with existing generic knobs.

This goal is measurement-only. It does not modify RTDL core/native code.

## Probe

Added:

```text
history/internal_docs/goal4911_point_location_prepare_tradeoff_probe.py
```

POD evidence:

```text
history/internal_docs/goal4911_point_location_prepare_tradeoff_summary_2026-07-03.json
```

Dataset:

```text
Australia lakes x parks representative Section 5.7 pair
```

The probe loads the CDBs once, then measures point-location prepare/run for:

- `default_current`
- `legacy_fixed8`
- `adaptive_ms8_e1.5`
- `block_merge64_i0_e1.5`
- `block_merge64_i1_e1.5`
- `default_current_repeat`

It records:

- prepare time;
- run time;
- native traversal timings;
- positive face count;
- FNV64 face hash for correctness consistency.

## Key Result

The current default is not obviously wrong. After warmup, it is competitive with
or better than the explicit modes tested.

### Warm default repeat

| Stage | prepare | run | traversal | face hash |
|---|---:|---:|---:|---|
| map0 in map1 | `0.260s` | `1.157s` | `0.010s` | matches |
| map1 in map0 | `4.043s` | `0.038s` | `0.002s` | matches |

### Selected comparison rows

| Mode | map0 prepare/run | map1 prepare/run | Correct hash? |
|---|---:|---:|---|
| default repeat | `0.260s / 1.157s` | `4.043s / 0.038s` | yes |
| legacy fixed8 | `0.213s / 10.915s` | `3.374s / 1.587s` | yes |
| adaptive ms8 e1.5 | `0.252s / 1.142s` | `4.073s / 0.040s` | yes |
| block_merge64 i0 e1.5 | `0.261s / 1.137s` | `4.325s / 0.036s` | yes |
| block_merge64 i1 e1.5 | `0.268s / 1.140s` | `4.439s / 0.037s` | yes |

Interpretation:

- `fixed8` reduces prepare slightly but makes run time explode; it is not a
  viable default.
- `adaptive` and `block_merge64` are similar to current default.
- The current default repeat is already near the best tradeoff among tested
  modes.
- The earlier high setup readings around `12s` are not stable enough to justify
  a default change.

## What This Rules Out

Goal4911 rules out:

```text
"Just change the group mode knob again"
```

as the next optimization.

The productized fine-grained/default route from Goal4894 remains valid.

## Remaining Setup Cost

There is still real setup cost:

```text
map1 in map0 prepare: about 4.0s in warm focused probe
```

But that cost appears to be the real cost of preparing a large directed
point-location locator / OptiX acceleration structure, not an obvious planner
mode mistake.

Further setup improvement would require a deeper generic feature:

- persistent prepared locator cache;
- reusable acceleration/build artifact across process runs;
- explicit service-style session lifecycle;
- or lower-level native build-time optimization.

Those are different from group-mode tuning and need separate approval.

## Boundaries

This goal does not claim:

- a new speedup;
- broad RayJoin performance;
- broad RTDL performance;
- full Section 5.7 performance;
- a change to LSI/PIP correctness;
- that point-location setup is solved.

It only claims that the current group-mode default should be retained based on
this focused tradeoff measurement.

## Recommendation

Retain the current default.

The next meaningful direction is not another mode sweep. It is either:

1. define a generic persistent prepared-locator/session-cache feature; or
2. pause performance work and consolidate the current best bounded results:

   ```text
   prepared-hot body: 3.918s
   writer:            1.840s
   byte_equal:         true
   ```

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. The goal tested the obvious knob before modifying code.

2. **What action would have made this stupid?**

   Changing the default based on one noisy `12s` setup reading without a focused
   tradeoff matrix.

3. **Was there another path?**

   Yes. Directly implementing locator persistence. That is larger and should not
   happen until simple knob explanations are ruled out.

4. **Can I start a different path that truly solves the problem?**

   Yes. If we continue setup work, it should be a generic persistent
   point-location session/cache design, not more planner knob tweaking.
