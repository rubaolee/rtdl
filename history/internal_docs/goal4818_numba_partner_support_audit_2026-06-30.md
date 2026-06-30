# Goal4818 Side Audit — v2.14 Numba Partner Support

Date: 2026-06-30

Status: `side_audit_complete_no_edits`

This side audit was delegated to a read-only explorer sub-agent while the main
thread continued Goal4818 correctness-gap diagnosis.

## Bottom Line

RTDL v2.14 supports Numba as an explicit partner for selected continuation
contracts, mainly post-RTDL column/row-stream work. It does **not** prove that
Numba is a general RayJoin Section 5.7 reproduction partner.

For RayJoin, Numba evidence is route-specific:

- compact-mask row filtering;
- topology/reference continuation;
- selected scalar/count references.

Full polygon overlay reproduction still depends on bundled RayJoin helper logic,
exact inputs, and unresolved correctness gaps.

## Timeline Summary

- Early roadmap: Numba appears as a future Python/partner candidate, not a
  finished API.
- Goal2025: proposes user-selected partners such as Triton/Numba.
- Goal2662: defines generic partner-continuation contracts; Numba is fallback or
  descriptor-level at that point.
- Goal2696: makes the partner matrix explicit; allowed partners include
  `python_reference`, `triton`, `numba`, and `cupy_conformance`; unsupported
  cells fail closed.
- Goal3002/Goal3003: add RayJoin Numba compact-mask wiring and L4 POD evidence
  for `pip`, `lsi`, and `overlay_seed`; parity passes, but claim flags remain
  false.
- Goal3052: confirms RayJoin compact-mask 1M-row selected partner evidence, plus
  other Numba lanes. It explicitly does not authorize release or broad speedup
  claims.
- Goal3835: stronger Numba evidence for RT-DBSCAN prepared-grid/component
  continuation.
- Goal3837: Barnes-Hut Numba exact-force is valid as a no-RawKernel reference,
  but slower than CuPy overall.
- Goal3921: guidance says RT-DBSCAN recommends Numba, while Barnes-Hut keeps
  CuPy default and exposes Numba as measured reference. No automatic partner
  selection.
- Goal4380 / v2.14 release docs: RayJoin public rows remain scoped; LSI/PIP are
  primitive-first scalar-count rows, while Section 5.7 overlay is a 2/8
  exact-input bundled app route, not full paper reproduction.

## API/Surface Summary

Public-ish Numba surfaces include:

- `numba_partner_available`
- `describe_numba_*`
- `run_numba_*`
- `execute_compact_mask_typed_stream_partner_columns`
- `filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`

RayJoin-specific Numba surfaces include:

- `describe_rayjoin_v2_6_numba_compact_mask_continuation`
- `run_rayjoin_v2_6_numba_compact_mask_preview`
- `run_rayjoin_v2_9_numba_side_aware_topology_reference`

These are app/reference routes, not complete generic Section 5.7 APIs.

Bundled RayJoin helper surfaces include:

- `run_rayjoin_overlay_rtdl_from_cdb_paths`
- `_run_lsi_rows`
- `_run_point_location_faces`
- `_PreparedPointLocationRunner`
- `_assemble_output_chains`

These are bundled helper/application logic, not proof of generic
primitive+Numba reproduction.

## Evidence And Limits

Goal3003/Goal3052:

- RayJoin compact-mask Numba over 1,000,000 rows passes for `pip`, `lsi`, and
  `overlay_seed`.
- CPU parity is true.
- It is post-RT `compact_mask_i64` continuation evidence only.
- It does not prove paper reproduction, whole-app speedup, RT-core speedup,
  true-zero-copy, or "RTDL beats RayJoin".

Goal4380:

- Section 5.7 overlay has 2/8 complete exact-ready pairs.
- County x Zipcode: author process wall 5.521s, RTDL OptiX 5.782s, Embree
  15.121s.
- Block x Water: author process wall 27.944s, RTDL OptiX 28.650s, Embree
  53.793s.
- This is process-wall/same-route evidence, not author hot-compute parity and
  not full Section 5.7.

Goal4817:

- clean system Python lacked Numba;
- bundled helper ran but did not byte-match the author public sample;
- author binary did byte-match the same answer.

Therefore Goal4818 is correctly a correctness-gap diagnosis, not a performance
or reproduction run.

## First-Class Status

For v2.14 overall:

`Numba is a first-class explicit partner choice for selected continuation
contracts and app-author guidance.`

For RayJoin Section 5.7:

`Numba is not a complete first-class reproduction route.`

It remains selected route-specific evidence. The full overlay path depends on
bundled helper/application logic, exact inputs, public row/coordinate API gaps,
and PIP tie-break correctness.

## Implication For Goal4816/Goal4818

Goal4816/Goal4818 should treat Numba as a continuation probe, not the complete
RayJoin reproduction engine.

The safe path remains:

- separate bundled-helper results from generic primitive+Numba attempts;
- do not patch RTDL/native code;
- do not use private helpers as public API;
- do not run Section 5.7 performance until correctness and route classification
  are resolved.

