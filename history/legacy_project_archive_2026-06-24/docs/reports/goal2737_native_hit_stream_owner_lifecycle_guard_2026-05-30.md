# Goal2737: Native Hit-Stream Owner Lifecycle Guard

Date: 2026-05-30
Status: accepted as lifecycle hardening

## Purpose

Claude's Goal2735 review accepted the same-pointer / zero-copy boundary audit with a critical remaining risk: native ownership lifetime is not enforced strongly enough for any future public true-zero-copy claim.

Goal2737 adds a narrow fail-closed lifecycle guard for native hit-stream outputs. It does not authorize true zero-copy. It makes the current experimental contract harder to misuse.

## Changes

- `RtdlNativeDeviceHitStreamOutput` now records an explicit `closed` state.
- `close()` is idempotent and marks the output closed after delegating to the owner close hook.
- `to_handoff()` now fails if the native output is already closed.
- `RtdlRawCudaColumn.__cuda_array_interface__` now fails if its owner chain is closed.
- Metadata now exposes:
  - `owner_lifetime_state`
  - `native_release_enforced_by_python_owner`
  - `handoff_after_close_allowed = false`
  - `owner_close_supported`

## Boundary

This is a Python-side guardrail. It does not prove:

- native release entrypoint correctness;
- CUDA stream synchronization;
- cross-partner ownership transfer;
- GPU-wide pointer stability;
- public true-zero-copy wording.

It does reduce a real misuse class: a caller cannot close a native hit-stream output and then create or adapt a new handoff from the stale pointers through the Python API.
