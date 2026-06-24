# Goal2833 Primitive Payload Partner Planner

Date: 2026-05-31

## Purpose

Goal2831 introduced typed primitive-payload column descriptors. Goal2833 adds the next layer: a partner-neutral planner that consumes those descriptors and the existing v2.5 partner support matrix, then returns either an accepted preview plan or a fail-closed fallback reason.

This is not an execution engine. It is an explainable planning contract for deciding whether a partner may safely consume a descriptor.

## New API

Added in `src/rtdsl/hit_stream_handoff.py`:

- `GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_PLANNER_VERSION`
- `GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_PLAN_STATUSES`
- `plan_primitive_payload_partner_continuation(operation, partner, descriptors)`

Exported through `rtdsl.__init__`.

## Planner Behavior

The planner:

- resolves partner aliases through `plan_v2_5_partner_support(...)`;
- requires descriptor metadata produced by Goal2831;
- checks support-matrix status;
- checks CUDA residency when required by the support cell;
- checks neutral-buffer seam presence when required;
- preserves same-stream/event-ordering requirements;
- respects descriptor fallback reasons;
- rejects descriptor-only partner cells as non-executable preview plans;
- never authorizes RT traversal replacement, public speedup, or true zero-copy claims.

## Validated Cases

`tests/goal2833_primitive_payload_partner_planner_test.py` covers:

- CuPy accepted preview for `hit_stream_grouped_ray_id_primitive_i64` with a CUDA same-stream descriptor.
- Accepted preview plans use machine-readable `plan_status: accepted_preview`.
- CuPy descriptor-only `segmented_count_i64` fail-closed with `partner_unavailable`.
- Triton `segmented_sum_f64` fail-closed on a host descriptor with `host_reference` and `stream_ordering_unproven`.
- Python reference accepts host descriptors as `reference_contract` without zero-copy claims.
- malformed descriptor metadata fails closed.

## Claim Boundary

`accept-with-boundary`

The accepted claim is narrow: RTDL can now explain whether a typed primitive payload descriptor is eligible for a specific partner preview path or must fall back, with explicit fallback reasons.

This does not authorize:

- arbitrary partner execution;
- replacing RTDL/OptiX traversal;
- broad true-zero-copy claims;
- public speedup claims;
- paper reproduction claims;
- whole-app acceleration claims;
- v2.5 release claims.

## Validation

Local focused suite:

```text
python -m unittest \
  tests.goal2833_primitive_payload_partner_planner_test \
  tests.goal2831_primitive_payload_column_descriptor_test \
  tests.goal2793_v2_5_partner_role_reconciliation_test \
  tests.goal2696_v2_5_partner_support_matrix_test
```

Result:

```text
Ran 20 tests in 0.028s
OK
```

## Next Step

The next runtime step is to attach this planner to real continuation entrypoints: when a user asks for CuPy/Triton/Numba consumption, RTDL should report the planner decision alongside execution metadata, including the exact fallback reason if it chooses a reference or app-chosen path.
