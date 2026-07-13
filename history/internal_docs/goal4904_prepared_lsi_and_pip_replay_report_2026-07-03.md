# Goal4904 — Prepared LSI + Prepared PIP Hot Replay Probe

Date: 2026-07-03

## Verdict

`completed_prepared_replay_probe__byte_equal__lsi_hot_replay_effective`

Goal4904 validated a generic RTDL prepared replay route:

```text
prepare CDB packed inputs
prepare public planar-map LSI base/query session
prepare public planar-map point-location/PIP sessions
→ replay the overlay body with prepared sessions
```

The result is a substantial hot-replay improvement:

- byte-for-byte correctness is preserved;
- hot body with prepared PIP sessions only (Goal4903) was `6.450s`;
- hot body with prepared PIP + prepared LSI query replay is `4.638s`;
- LSI pair-id rows drop from `1.814s` to `0.006s` in the hot replay;
- the result is bounded to repeated-query/hot-replay workloads, not single-run cold execution.

No RTDL LSI/PIP semantics changed. No RayJoin-specific hidden kernel was added.

## Files Added

- `history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py`

No product runtime/native files were changed in this goal.

## Evidence

- Goal4904 prepared replay summary:
  - `history/internal_docs/goal4904_prepared_lsi_pip_replay_summary_2026-07-03.json`
- Goal4903 buffered writer hot-session baseline:
  - `history/internal_docs/goal4903_buffered_writer_hot_session_summary_2026-07-03.json`

## Setup Cost

Goal4904 setup phases:

| Setup phase | Time |
|---|---:|
| import Goal4886 wrapper | `3.023s` |
| load/pack left | `2.316s` |
| load/pack right | `2.482s` |
| prepare LSI base | `0.744s` |
| prepare LSI query | `0.691s` |
| prepare point-location map0 in map1 | `1.392s` |
| prepare point-location map1 in map0 | `13.864s` |
| destroy reused sessions | `0.333s` |

The setup cost is still real. The large-map PIP preparation remains the major cold/setup cost.

## Hot-Replay Result

Clean comparison: Goal4903 repeat 1 vs Goal4904 repeat 1.

| Metric | Goal4903 buffered writer + PIP session reuse | Goal4904 prepared LSI + PIP replay | Speedup |
|---|---:|---:|---:|
| hot body total | `6.450s` | `4.638s` | `1.39x` |
| LSI pair-id rows | `1.814s` | `0.006s` | `~294x` |
| output writer | `2.587s` | `2.562s` | unchanged |
| vertex PIP map0 in map1 | `1.089s` | `1.096s` | unchanged |

Correctness:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276320
bytes: 6189260
```

## Interpretation

This proves that the public prepared LSI query session is valuable when the same LSI query is replayed against the same prepared base/query pair. It turns LSI from a multi-second phase into a millisecond-level replay phase.

This does not mean the single-run paper reproduction avoids LSI setup. It means RTDL has a real prepared-replay shape for repeated-query workloads.

The hot replay is now dominated by:

1. output writer: `2.562s`;
2. vertex PIP map0 in map1: `1.096s`;
3. reprojection + sorting: about `0.883s`;
4. LSI replay: `0.006s`.

## What This Does Not Claim

This goal does not claim:

- single-run speedup over AuthorOfficial;
- broad RTDL/RayJoin speedup;
- full eight-pair Section 5.7 performance;
- LSI/PIP semantic changes;
- Numba on RTDL primitive traversal;
- raw callback or OptiX shader exposure;
- V3/V4 release resurrection.

## Next Engineering Target

For hot replay, LSI is no longer the target. The next measured target is output-chain construction/emission, but a further Python micro-optimization is unlikely to be enough.

If continuing app-layer performance work, the next goal should be structural:

> Design and test a compiled/partner-assisted output-chain construction path that preserves the AuthorOfficial output contract and keeps RTDL primitives untouched.

If continuing engine work, the next goal should instead address cold/setup cost:

> Reduce or persist the large point-location base prepare cost generically.

The immediate evidence says the hot replay bottleneck is the writer; the cold/setup bottleneck is point-location base preparation.

## Goal-Level Decision Audit

1. Did I make a stupid decision?
   - No. I chose the next generic prepared-session lever instead of doing more writer micro-tuning.
2. What actions would have made it stupid?
   - Claiming prepared replay as a single-run benchmark win, or caching the actual output rather than replaying public RTDL primitives.
3. Was there another path?
   - Yes: compiled writer work. It remains relevant, but prepared LSI replay was already a public RTDL capability and had a strong measured basis from Goal4898.
4. Did I correct course?
   - Yes. The result is reported as hot replay only, with setup cost shown separately.
