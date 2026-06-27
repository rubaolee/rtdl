# Goal2835: Primitive Payload Entrypoint Metadata

Date: 2026-05-31

Status: implemented locally, pending external review at initial write

## Purpose

Goal2833 added a partner-neutral planner for typed primitive payload columns, but the planner was still a separate surface. A user could inspect a plan, then call a continuation entrypoint, but the continuation result did not necessarily carry the same explanation.

Goal2835 attaches that planner decision to real continuation entrypoints so the v2.5 runtime can answer:

- which continuation entrypoint was called;
- which partner was requested and resolved;
- whether the plan is `accepted_preview`, `reference_contract`, or `fallback_required`;
- why fallback is required, when it is required;
- whether stream ordering was preserved;
- whether any public speedup, true-zero-copy, or RT-traversal replacement claim is authorized.

## Implementation

Code changes:

- `src/rtdsl/hit_stream_handoff.py`
  - Adds `GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_ENTRYPOINT_METADATA_VERSION`.
  - Adds `describe_primitive_payload_partner_continuation_entrypoint(...)`.
  - Adds `attach_primitive_payload_partner_continuation_metadata(...)`.
  - Keeps all planner output claim-bounded: no public speedup claim, no true-zero-copy claim, no RT traversal replacement.
- `src/rtdsl/partner_continuation_protocol.py`
  - Extends `execute_v2_5_partner_continuation_reference(...)` with optional `primitive_payload_descriptors`.
  - When descriptors are supplied, the reference result now carries `primitive_payload_continuation_entrypoint` and `primitive_payload_continuation_plan`.
- `src/rtdsl/triton_partner_continuation.py`
  - Extends `run_triton_partner_continuation(...)` with optional `primitive_payload_descriptors`.
  - When descriptors are supplied, the dispatcher attaches planner metadata to both preview results and explicit reference-fallback results.
  - This does not change kernel execution, block sizing, validation mode, or fallback behavior.
- `src/rtdsl/__init__.py`
  - Re-exports the new descriptor helpers.

## Contract Behavior

The new metadata is explain/fail-closed metadata only.

Reference entrypoint:

- host descriptors can still execute the Python reference contract;
- the attached plan reports `reference_contract`;
- no zero-copy or speedup claim is authorized.

Triton dispatcher:

- if a supplied descriptor/operation/partner combination is not executable under the support matrix, the result records `fallback_required` and explicit reasons;
- descriptor-only or unsupported partner cells remain fail-closed unless the caller explicitly asked for reference fallback;
- successful preview paths can attach `accepted_preview` without being promoted.

Prepared same-stream CuPy graph consumer:

- `describe_primitive_payload_partner_continuation_entrypoint(...)` can describe the Goal2829 same-stream graph partial consumer as `accepted_preview` for the narrow CuPy conformance cell;
- this remains an internal preview path and does not authorize public claims.

## Boundaries

Goal2835 deliberately does not:

- add a new primitive;
- change native kernels;
- change Triton/CuPy/Numba execution semantics;
- claim true zero-copy;
- claim public performance speedup;
- claim v2.5 release readiness.

The value is traceability: the planner decision visible at the planning layer is now also visible where users and tests inspect actual continuation outputs.

## Validation

New test:

- `tests.goal2835_primitive_payload_entrypoint_metadata_test`

Focused test intent:

- Python reference continuation results expose `reference_contract` planner metadata.
- Triton dispatcher explicit fallback results expose `fallback_required` planner metadata.
- Planned CuPy same-stream graph partial entrypoint metadata reports the narrow `accepted_preview` cell.
- Source remains generic and claim-bounded.

## Verdict

Codex local verdict: `accept-with-boundary`.

Goal2835 is accepted as a traceability hardening step. It moves v2.5 closer to a user-explainable RTDL+partner runtime, but it is not a performance promotion or release gate by itself.
