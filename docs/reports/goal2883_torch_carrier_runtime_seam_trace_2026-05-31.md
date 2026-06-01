# Goal2883 Torch Carrier Runtime Seam Trace

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Claude's Goal2881 review accepted Goal2879's torch-carrier provenance hardening
but kept one release-watch item: the guard proved metadata/contract provenance,
not execution-time dataflow. Goal2883 adds a narrow runtime seam trace for the
bounded Triton torch-carrier gather path.

## Implementation

Updated:

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2883_torch_carrier_runtime_seam_trace_test.py`

New surface:

- `trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority(...)`

The trace creates neutral-buffer leases for the three columns consumed by the
Triton carrier gather path:

- `primitive_ids`
- `primitive_group_ids`
- `primitive_values`

Each lease records:

- `handoff_begin`
- `continuation_complete`
- `authority_origin: neutral_buffer_seam`
- `carrier_authority_disallowed_by_contract: true`

`_gather_payload_torch_carrier(...)` now records this trace in
`torch_carrier_execution.neutral_seam_runtime_authority_trace` when the carrier
path executes.

## Boundary

This is runtime provenance for the bounded Triton carrier path. It does not
remove the carrier, does not prove true zero-copy, does not prove performance,
does not authorize Triton auto-selection, and does not authorize release.

It narrows the Goal2881 release-watch item from "metadata only" to "metadata plus
runtime seam lease trace for the current carrier gather path."
Future promoted partner paths still need their own runtime traces.

Goal2883 is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not true-zero-copy wording,
and not package-install wording.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2883_torch_carrier_runtime_seam_trace_test \
  tests.goal2882_goal2881_claude_review_intake_test \
  tests.goal2879_torch_carrier_seam_authority_provenance_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 20 tests in 0.425s
OK (skipped=1)
```

Pod validation from pushed `main`:

```text
commit: 920df6a6
scope:
  tests.goal2883_torch_carrier_runtime_seam_trace_test
  tests.goal2882_goal2881_claude_review_intake_test
  tests.goal2879_torch_carrier_seam_authority_provenance_test
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 20 tests in 1.620s
OK
```

The pod run did not skip the torch execution-path test, so
`torch_carrier_execution.neutral_seam_runtime_authority_trace` was exercised in
the runtime path.

## Codex Verdict

`accept-with-boundary`
