# Goal4981: Promote Reversed Side Order For Writer-Free Binary Descriptor Route

Date: 2026-07-04

## Purpose

Goal4980 proved that reversing compiled carrier side order from `0,1` to `1,0` materially reduces the writer-free binary descriptor route while preserving descriptor-consumer structural anchors.

Goal4981 promotes that policy for the writer-free binary descriptor route only.

## Work

- Change the default `--compiled-group-side-order` to `1,0`.
- Keep CLI override for `0,1` or `1,0`.
- Record the selected side order in claim boundary and carrier metadata.
- Explicitly state that this is not a paper-text ordering policy.
- Run POD top4 with default route and compare against the Goal4980 `1,0` diagnostic.

## Verification

Required:

- local tests confirm default and claim boundary
- POD top4 artifact shows default order `1,0`
- structural anchors remain valid
- writer-free hot/downstream floor are in the Goal4980 `1,0` range

## Boundary

Allowed:

- app-owned binary-route policy
- no core/native changes

Forbidden:

- no paper byte-equality claim for this route
- no author-performance headline
- no RTDL core promotion
- no Layer 4 fusion

## Exit Labels

- `completed_reversed_side_order_promoted_for_binary_route`
- `fail_redo_due_to_structural_mismatch`
- `fail_redo_due_to_paper_text_order_overclaim`
