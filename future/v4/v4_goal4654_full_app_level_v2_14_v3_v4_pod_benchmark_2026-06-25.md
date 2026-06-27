# V4 Goal4654 Full App-Level V2.14 / V3.0.2 / V4 POD Benchmark

Date: 2026-06-25
Status: evidence collected, not release authorization

Raw evidence directory:

```text
future/v4/evidence/v4_goal4654_serious_20260625_2/
```

Runner:

```text
scripts/v4_goal4654_full_app_level_pod_benchmark.py
```

## What Was Run

This run executed the four Goal4653 frozen full-route app rows across three
source trees on the supplied RTX A5000 POD:

- `v2.14` tag archive
- `v3.0.2` tag archive
- current V4 candidate tree

The serious profile used:

- RTDBSCAN: `clustered3d`, `262144` points, repeat `5`, warmup `1`.
- RayDB-style: `131072` generated rows, `1024` groups, repeat `7`, warmup `2`.
- Triangle counting: `32768` K4 cliques, `196608` binary edges, repeat `7`, warmup `2`.
- LibRTS spatial index: `1000000` boxes, `1000` queries, operation `all`, repeat `240`, warmup `1`.

RTDBSCAN large performance rows used `--no-validation` because the first attempt
with full large validation spent minutes in CPU/reference preparation, reached
44GB RSS, and never entered the GPU hot path. The runner therefore added a
separate same-route `2048` point parity companion for each version.

## Important Provenance Blocker

V2.14 and V3.0.2 Embree libraries were built in their tag trees. Their OptiX
libraries could not be built on this POD because OptiX SDK headers are absent.
For OptiX-dependent old-version rows, the runner used a declared V4
compatibility `librtdl_optix.so`.

This blocks pure tag-native V2/V3/V4 release authorization from Goal4654 alone.
Goal4655 must keep this visible.

## Scorecard

| App | V4/V2.14 hot | V4/V3.0.2 hot | V3.0.2/V2.14 hot | RC OK | Parity |
| --- | ---: | ---: | ---: | --- | --- |
| `rt_dbscan` | 1.070x | 1.084x | 0.987x | true | true |
| `raydb_style` | 0.994x | 1.000x | 0.995x | true | true |
| `triangle_counting` | 15.548x | 1.117x | 13.924x | true | true |
| `librts_spatial_index` | 0.999x | 1.001x | 0.997x | true | true |

## Interpretation

This is a real app-level run, but it does not support a broad
"formal high-performance V4" claim.

- RTDBSCAN shows a modest V4 hot-path gain over V2.14/V3.0.2, not a 1.20x pass.
- RayDB-style is effectively parity at app level.
- LibRTS is effectively parity at app level.
- Triangle counting is the only large V4/V2.14 win, but most of that change
  already exists by V3.0.2; V4/V3.0.2 is only 1.117x.

The honest next step is Goal4655 analysis with the partner-migration lock and
native-provenance blocker preserved. No public app-level speedup wording should
be written from this file alone.

## Goal-Level Decision Audit

1. Was I being stupid?
   - The first serious run was becoming stupid: it let RTDBSCAN large validation
     consume CPU/RAM without entering the measured hot path.
2. If yes, what action made it stupid?
   - I initially tied large correctness validation and hot-path performance into
     one command for RTDBSCAN.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: split large performance timing from same-route small parity evidence,
     and record that split instead of pretending it is full large correctness.
4. Can I now try the different path that actually solves the problem?
   - Yes. The final run used large no-validation performance rows plus parity
     companions, and the report records the limitation explicitly.

## Non-Authorization

Goal4654 does not authorize V4 release, public V4 speedup wording, broad
whole-app claims, CuPy blanket claims, arbitrary Numba callback claims, C ABI,
embedding, or true-zero-copy claims.
