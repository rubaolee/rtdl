# Goal2046 CuPy Witness Continuation Surface

Date: 2026-05-14

Status: `accept-with-boundary`

## Purpose

Goal2044 added the NumPy reference contract for generic partner continuations.
Goal2046 adds the matching CuPy-facing surface for the witness-carrying slice:

- `cupy_group_topk`
- `cupy_group_argmin_then_global_argmax_with_witness`
- `directed_hausdorff_2d_cupy_columns`

This prepares the exact Hausdorff-with-witness contract for pod validation without changing the RTDL native engines.

## Design

The CuPy functions mirror the NumPy reference names and semantics:

- group by generic group id;
- rank by score with deterministic item-id tie-break;
- choose per-group argmin;
- choose global argmax over those per-group minima;
- return witness ids and metadata.

The contract remains app-agnostic. The primitive names do not mention facility, ANN, Hausdorff, road, robot, or overlay. `directed_hausdorff_2d_cupy_columns` is the first app-facing adapter, but it is built from the generic witness-continuation primitive.

## What This Enables

- pod tests can exercise exact Hausdorff witness extraction on CuPy;
- future OptiX zero-copy candidate-row work has a partner-side continuation target;
- v2.0 can explain the difference between fast threshold decisions and rich exact witness extraction.

## Boundary

This is not yet release performance evidence.

Current boundaries:

- no pod runtime evidence has been collected for these CuPy functions;
- no OptiX zero-copy candidate-row handoff feeds this exact witness contract yet;
- this does not make exact Hausdorff a large-scale v2.0 speedup claim;
- this does not solve exact facility K=3 ranking, exact ANN recall optimization, or polygon overlay.

## Next Step

Run pod validation for:

1. `directed_hausdorff_2d_cupy_columns` correctness against the NumPy reference;
2. exact Hausdorff app timing with `partner_exact --partner cupy`;
3. future same-contract OptiX candidate-row handoff once available.

## Verdict

`accept-with-boundary`
