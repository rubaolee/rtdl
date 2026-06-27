# Goal4408 V3.0 M12 No-Hidden-Copy Contract

Date: 2026-06-15

Status: complete for the app-agnostic internal contract layer.

## Purpose

M11 produced one measured pod artifact for the fixed-radius grouped-union pilot. M12 turns that evidence shape into a reusable RTDL V3 contract so future benchmark apps can be checked with the same rule instead of copying M11-specific validation code.

The contract answers one narrow question:

During a measured native-to-partner continuation window, did RTDL secretly move named handoff/output columns through host memory or rematerialize them through unexpected CUDA copies?

## Added API

Module:

- `src/rtdsl/v3_0_no_hidden_copy_contract.py`

Public exports:

- `CudaTransferCounter`
- `classify_no_hidden_copy_transfer_snapshot`
- `min_named_column_bytes_from_descriptors`
- `annotate_no_hidden_copy_metadata`
- `summarize_no_hidden_copy_classifications`
- `validate_no_hidden_copy_classification`
- `validate_no_hidden_copy_row`
- `validate_no_hidden_copy_payload`

## Contract Rule

A row is internally no-hidden-copy ready only when all are true:

- same-stream handoff evidence exists.
- transfer-counter evidence exists for the measured window.
- device-to-host copy calls are zero.
- device-to-device copy calls are zero.
- unknown-direction copy calls are zero.
- host-to-device bytes are at most the small non-column allowance, currently 4,096 bytes.
- host-to-device bytes are below the smallest declared named-column byte size.
- public claim flags remain false.

The small HtoD allowance is for non-column setup such as launch parameters. It is not permission to move data columns.

## M11 Integration

M11 keeps its user-facing names and runner, but its classifier, metadata annotation, and row/payload validation now delegate to the M12 contract layer. This keeps the existing pod artifact valid while making the no-hidden-copy gate reusable for RayJoin, RTNN, DBSCAN, and later app-specific V3 work.

## Claim Boundary

Allowed internal wording:

RTDL has an app-agnostic internal contract for checking that a measured native-to-partner continuation window does not contain hidden named-column host/device movement.

Disallowed public wording:

- Do not turn M12 alone into a public speedup claim.
- Do not claim an app is zero-copy until that app has its own measured transfer-counter artifact.
- Do not claim end-to-end I/O is zero-copy unless the measured window covers end-to-end I/O.
- Do not treat a small launch-parameter HtoD copy as column movement.

## Validation

The M12 test gate covers:

- accepting small non-column launch-parameter HtoD transfer;
- rejecting DtoH, DtoD, unknown, large HtoD, and named-column-scale HtoD transfer shapes;
- validating synthetic app-agnostic payloads;
- validating the tracked M11 pod artifact through the generic M12 validator;
- rejecting accidental public claim promotion.
