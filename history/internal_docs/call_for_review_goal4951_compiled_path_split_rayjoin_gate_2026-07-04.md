# Call For Review: Goal4951 Compiled Path-Split RayJoin Gate

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md`
- `history/internal_docs/goal4951_section57_compiled_path_split_adapter.py`
- `history/internal_docs/goal4951_compiled_path_split_spike.py`
- `history/internal_docs/goal4951_pod_artifacts/plain_section57_overlay.json`
- `history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_first.json`
- `history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_rerun.json`

Requested verdict:

`approve_goal4951_correct_but_not_faster_stop`

or, if blocked:

`block_goal4951_close_until_amended`

## Context

Goal4951 Gate A/B passed and authorized Gate C.

Gate C/D then wired the internal compiled generic path-split materializer into
the RayJoin Section 5.7 public-sample app as an app adapter. The route preserved
byte equality but missed the writer performance gate.

The approved kill condition was:

> If byte-equal but slower, the route is killed and not retained as default.

This packet asks whether Goal4951 should now close as
`compiled_path_split_correct_but_not_faster_stop`.

## Questions

1. Does the compiled adapter preserve the intended boundary: generic materializer
   owns only path-split rows, while RayJoin app owns descriptors and final text
   formatting?

2. Does the evidence support Gate C passing: byte-for-byte equality to the public
   answer on the plain, compiled first-run, and compiled rerun outputs?

3. Is the performance comparison fair enough for Gate D: same POD, same data,
   same cache, same answer, plain writer versus compiled route?

4. Does Gate D clearly fail the approved threshold?

   - plain writer: `2.583328s`
   - compiled rerun writer: `4.155936s`
   - relative speed: `0.622x`
   - required minimum: `>= 1.10x`

5. Should the compiled path-split route be killed as default and retained only as
   internal experimental evidence?

6. Does the packet avoid overclaiming that all Layer 3 work is impossible, while
   correctly rejecting this specific CPU/Numba materializer route?

7. Is any further test required before closing Goal4951, or is the kill condition
   already satisfied?

## Non-Authorization Boundary

Approval does not authorize:

- public API exposure;
- default route promotion;
- new Layer 3 implementation;
- broad performance claims;
- further RayJoin performance work without a new reviewed goal.
