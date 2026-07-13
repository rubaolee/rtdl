# Goal4862: Chain 41230 Output-Chain Face Assignment Diagnostic

Date: 2026-07-02

Depends on:

- Goal4860: LSI row materialization repaired.
- Goal4861: Section 5.7 re-entry classified the remaining first difference as
  output-chain face assignment.

## Purpose

Diagnose the first Section 5.7 County x Zipcode fallback-helper mismatch without
running another blind full overlay.

First difference:

```text
author: 41230 2 42104 42105 280 290
rtdl:   41230 2 42104 42105 294 295
```

The chain id and point ids match.  Only the final face ids differ.

## Questions

1. Are `280/290` and `294/295` merely different dynamic output-face numbering
   labels for the same underlying face-pair semantics?
2. Or does RTDL assign a different underlying midpoint/other-map face before
   final output-face renumbering?
3. Does the problem come from:
   - midpoint point-location;
   - face-id creation order;
   - output-chain polygon-id propagation;
   - scaled/rational midpoint coordinate handling?

## Allowed Work

- inspect author output around line 123678;
- inspect RTDL output-chain generation for chain 41230 and nearby chains;
- add diagnostic-only scripts under `history/internal_docs`;
- use small slices or focused probes before any full rerun;
- call private bundled helper internals only as diagnostics, clearly labeled.

## Forbidden Work

- no performance run;
- no public docs/tutorial edits;
- no claim of Section 5.7 correctness;
- no relabeling bundled-helper diagnostics as generic public-language evidence.

## Exit Labels

- `diagnosed_face_id_renumbering_only`
- `diagnosed_midpoint_point_location_mismatch`
- `diagnosed_output_chain_polygon_id_mismatch`
- `diagnosed_scaled_coordinate_midpoint_mismatch`
- `blocked_need_author_instrumentation`
