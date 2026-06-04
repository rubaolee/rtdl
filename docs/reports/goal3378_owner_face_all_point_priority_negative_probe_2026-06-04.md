# Goal3378: Owner-Face All-Point Priority Negative Probe

Date: 2026-06-04

## Status

Goal3378 tests whether the seven-point owner-face route can be promoted by applying a generic-looking priority rule to all 512 points in the bounded county slice.

The policy under test is `incident_chain_length_rank`:

1. prefer incident faces supported by fewer short chains;
2. then prefer faces with larger minimum incident-chain length;
3. then break by face id.

This is caller/data policy over CDB-derived incident rows. It is not native engine logic.

## Result

The policy must be rejected for default route use.

Artifact:

`docs/reports/goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.json`

Measured on the RTX A5000 pod:

- commit: `75876b18c45fe3c22edaa616198b2e35f4ceefb4`
- GPU: `NVIDIA RTX A5000, 580.126.09`
- CuPy: `14.1.1`
- point count: `512`
- shape count: `478`
- incident rows: `1507`
- priority rows: `1507`
- OptiX live candidate rows: `1429`
- exact prepared rows: `1417`
- filtered rows after the all-point owner-face policy: `1007`
- missing exact rows: `410`
- extra rows: `0`
- `matches_exact: false`
- `policy_result: reject_for_default_route`

The rule removes extras but is too aggressive: it drops true exact rows, including the first missing sample `(260, 260)`.

## Why This Matters

Goal3376 proved the live OptiX candidate stream plus CuPy owner-face continuation works for the seven known boundary-extra points. Goal3378 proves the current priority signal cannot simply be widened to all points.

That keeps the route honest:

- the live candidate stream is real;
- the owner-face continuation is useful for known boundary ambiguity;
- route-scale promotion still needs a better ambiguity-detection or priority-policy contract;
- native/default route claims remain blocked.

## Boundary

This negative probe does not authorize release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true-zero-copy, or native default route claims.

All claim-boundary flags in the JSON are `false`.

## Next Engineering Implication

The next viable path is not "filter every candidate row." It should be one of:

- a selective ambiguity-set contract where only points requiring owner-face reconciliation are filtered;
- a stronger generic boundary-topology policy that preserves non-ambiguous true positives;
- a route-level validated fallback that uses live candidate columns plus exact rows only when the policy cannot prove correctness.

