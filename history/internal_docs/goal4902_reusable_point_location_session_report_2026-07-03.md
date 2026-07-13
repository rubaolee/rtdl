# Goal4902 — Reusable Prepared Point-Location Session Probe

Date: 2026-07-03

## Verdict

`completed_reusable_point_location_session_probe__hot_body_speedup_valid__single_run_setup_not_removed`

Goal4902 validated the generic RTDL prepared point-location session pattern:

```text
prepare planar-map point-location base sessions once
→ run repeated point-location queries / overlay bodies
→ destroy sessions when the application is done
```

The result is useful and bounded:

- byte-for-byte correctness is preserved;
- the hot overlay body with reused point-location sessions runs in `6.915s`;
- the comparable Goal4901 steady-state body that prepared point-location inside each run was `11.320s`;
- hot-body speedup from session reuse is about `1.64x`;
- this does not remove single-run setup cost; it makes the cost explicit and amortizable for repeated-query workloads.

No RTDL LSI/PIP semantics changed. No RayJoin-specific hidden kernel was added.

## Files Added

- `history/internal_docs/goal4902_reusable_point_location_session_probe.py`

No product runtime files were changed in this goal.

## Evidence

- Probe summary:
  - `history/internal_docs/goal4902_reusable_point_location_session_summary_2026-07-03.json`
- Prior steady-state reference:
  - `history/internal_docs/goal4901_phase_accounting_summary_2026-07-03.json`
  - `history/internal_docs/goal4901_accounted_harness_verify_summary_2026-07-03.json`

## What Was Measured

The probe:

1. imports the existing public-primitives Numba wrapper;
2. loads the Australia representative CDBs using the packed cache;
3. prepares both public planar-map point-location sessions once;
4. runs the public LSI + public PIP + Numba app-continuation overlay body twice while reusing the prepared point-location sessions;
5. verifies output byte equality to AuthorOfficial each run.

This is a hot-session route. It is not presented as a single-run cold benchmark.

## Setup Cost

Setup phases from the POD run:

| Setup phase | Time |
|---|---:|
| import Goal4886 wrapper | `3.741s` |
| load/pack left | `3.564s` |
| load/pack right | `0.660s` |
| prepare point-location map0 in map1 | `1.834s` |
| prepare point-location map1 in map0 | `9.190s` |
| destroy reused point-location sessions | `0.229s` |

Interpretation:

- Setup is still real.
- The large-map point-location base prepare remains expensive.
- Goal4902 does not pretend this cost disappeared.
- The value is that this setup can be paid once when the workload naturally issues repeated queries against the same planar maps.

## Hot Body Results

| Route | Total hot body | Correct |
|---|---:|---|
| Goal4901 steady repeat, prepares point-location each run | `11.320s` | yes |
| Goal4902 repeat 1, reuses point-location sessions | `6.915s` | yes |

Derived hot-body speedup:

```text
11.320 / 6.915 = about 1.64x
```

Goal4902 repeat 1 details:

| Phase | Time |
|---|---:|
| LSI public pair-id rows | `1.819s` |
| intersection reprojection | `0.468s` |
| sort map0+map1 | `0.408s` |
| vertex PIP map0 in map1 | `1.086s` |
| vertex PIP map1 in map0 | `0.028s` |
| midpoint generation/pack/PIP/assign | `0.029s` |
| output writer | `3.031s` |
| file summaries | `0.046s` |
| total | `6.915s` |

Output correctness:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

## Engineering Interpretation

This goal answers the question raised by Goal4901:

> Is reusable point-location preparation a real generic route?

Answer:

> Yes, for repeated-query / service-style workloads. The existing public prepared point-location session can be reused safely and yields a measured hot-body improvement.

But it also answers the harder question:

> Does this make single-run RayJoin overlay comparable to the author hot kernel?

Answer:

> No. The setup cost remains real, and the author still has a much more fused hot path. This goal only proves an amortization path for repeated use.

## Current Remaining Hot Bottlenecks

After point-location session reuse, the hot body is dominated by:

1. output writer: `3.031s`;
2. LSI public pair-id rows: `1.819s`;
3. vertex PIP map0 in map1: `1.086s`;
4. sorting/reprojection: about `0.876s`.

This means the next single hot-body optimization should not be point-location preparation. It should be either:

- a writer/output-chain bulk emission path; or
- another LSI row/refinement reduction; or
- a deeper dataflow fusion design, if the goal is to approach the author fused-kernel hot path.

For immediate evidence-based engineering, the writer is now the largest hot-body phase.

## What This Does Not Claim

This goal does not claim:

- a single-run speedup over AuthorOfficial;
- broad RayJoin speedup;
- full eight-pair Section 5.7 performance;
- LSI/PIP traversal speedup;
- Numba on RTDL primitive traversal;
- any change to the AuthorOfficial correctness contract;
- V3/V4 release resurrection.

## Goal-Level Decision Audit

1. Did I make a stupid decision?
   - No. I first verified whether the public point-location API already had a reusable session shape instead of inventing a new runtime feature.
2. What actions would have made it stupid?
   - Calling this a single-run improvement or pretending setup cost vanished.
3. Was there another path?
   - Yes: build a persistent native cache immediately. That would be more invasive and not yet justified before proving session reuse.
4. Did I correct course?
   - Yes. The goal uses existing generic prepared sessions, measures setup separately from hot body, preserves correctness, and identifies the next real bottleneck.
