# Codex Phoenix V3 Route Capability Map 2-AI Consensus

Status: accepted with required amendments applied, not release authorization.

Date: 2026-06-20.

## Consensus Inputs

Codex route map:

```text
docs/rebuild/v3/phoenix_v3_p0_route_capability_map_2026-06-20.json
```

External AI review:

```text
docs/reviews/claude_phoenix_v3_route_capability_map_review_2026-06-20.md
VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS
```

Verification:

```text
py -3 -m unittest tests.v3_phoenix_route_capability_map_test tests.v3_release_wording_gate_test
py -3 scripts\v3_release_wording_gate.py --pretty
```

Both passed after amendment intake.

## Decision

Codex and Claude accept the route-to-generic-capability map as the current
Phoenix planning map.

This map is not release evidence:

```text
Phoenix M7-qualified release rows: 0
release_authorized: false
public_speedup_claim_authorized: false
```

## Required Amendments Applied

| Claude requirement | Applied change |
| --- | --- |
| The map must be cited downstream as planning evidence only, with zero M7-qualified release rows. | Added `downstream_reference_rule` fields and README wording. |
| P1 subset rows must not produce unlabeled narrow geomeans. | Added explicit subset-geomean downstream rule for `threshold_summary`, `aabb_candidate_stream`, and `collision_flag_stream`. |
| Denominator discipline must be enforced, not implied. | Route-map tests and wording gate now require the downstream reference and subset-geomean rules. |

## Current Route Map Facts

- 19 OptiX-vs-Embree ratio rows covered.
- 10 promoted apps covered.
- 0 rows without a named generic capability.
- 0 M7-qualified release rows.
- 46-row V2.14-vs-V3 denominator remains the broad-population denominator.
- Barnes-Hut remains `P0_blocked` because paired V3-vs-V2 timing regressed.

## Goal-Level Decision Audit

Decision: accept the amended route map as the input to focused pod work.

1. Was I foolish?

   The corrected decision is not foolish. It prevents cherry-picking and forces
   every row to instantiate a generic V3 capability.

2. What actions would have made it foolish?

   Dropping weak rows from the denominator, hiding Barnes-Hut regression, or
   treating P1 subset geomeans as broad V3 performance would have been foolish.

3. Was there another path?

   Yes. I could have selected the biggest OptiX speedup rows and gone straight
   to pod reruns. That would repeat the old benchmark-first failure.

4. Can I now try a different path that actually solves the problem?

   Yes. The next pod work can be selected by Goal4392 capability gap rather
   than by impressive-looking ratios.

## Final Consensus Statement

The route map is accepted as a Phoenix planning artifact. It is the right input
for focused P0 work because it covers every app, maps every row to a generic V3
capability, preserves the broad denominator, and blocks release wording.
