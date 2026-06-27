# Phoenix V3 Redesign Step 0 Freeze

Status: `step0_frozen_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_paired_runs_status: paused_until_runtime_trunk_executes
runtime_trunk_status: not_yet_executing
```

This file records the repo-visible start of the Phoenix V3 redesign in
`docs/rebuild/v3/proposed_v3_redesign_build_the_runtime_trunk_first_2026-06-22.md`.
It is a freeze/control artifact, not a release artifact.

## Step 0 Decisions

| Item | Decision |
| --- | --- |
| Cache / prepared-query thread | Closed as hygiene only. Keep landed parity repairs; do not chase more as V3 core progress. |
| Set A / Set B | Frozen before the next full paired run in `docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json`. |
| Scorecard | The two-number Set-A / Set-B scorecard is the only release read. |
| Full all-app paired runs | Paused until the runtime trunk executes on Step-1 probes. |
| Partial M4.1 OptiX prepared-query route | Paused and explicitly not counted as Step-1 progress. |

## Current Gate Facts

- Current scorecard: `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- Set A geomean: `1.013x`
- Set B geomean: `1.007x`
- Focused material productized probes: `1 / 2`
- Full all-app pod spend authorized now: `false`

## Runner Guard

`scripts/phoenix_v3_serious_paired_v2x_runner.sh` now refuses to start by
default. It requires both:

```text
PHOENIX_V3_ALLOW_ALL_APP_RUN=1
PHOENIX_V3_RUNTIME_TRUNK_EXECUTED=1
```

Those variables are not a release authorization. They are a future Step-5
operator gate after Step 1 and Step 2 have produced focused evidence.

## Next Step

Step 1 is the only allowed engineering direction: make one residency-rich
family execute end to end through the productized runtime trunk. The first
candidate remains fixed-radius self-query to grouped-stream continuation,
because it maps to RTDBSCAN and can later generalize to RTNN/RayDB-style
grouped stream work.

## Goal-Level Decision Audit

1. Was I foolish?
   No for this decision.
2. If yes, what actions made the decision foolish?
   It would be foolish to keep tuning per-route caches, complete the paused
   M4.1 prepared-query route as if it were V3 core progress, or run the
   all-app suite before `runtime_executed` is true on Step-1 probes.
3. Was there another path?
   The old path was to chase parity/regression repairs and then average them
   into a blended geomean. That already produced `1.012x` and does not solve
   V3.
4. Can I now try a different path that solves the problem?
   Yes. Build one runtime trunk probe first, measure its own material gain and
   residency, then generalize before spending all-app pod time.

## Non-Authorization

This Step 0 freeze authorizes no release, no broad V3-over-V2.x wording, no
true-zero-copy wording, no V4/embedding work, and no public speedup claim.
The release gate remains `redo_required`.
