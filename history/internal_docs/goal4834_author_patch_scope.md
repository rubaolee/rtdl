# Goal4834 Author Patch Scope

Date: 2026-06-30

Patch:

- `history/internal_docs/goal4834_author_sos_t_reported.patch`

## Scope

The patch is intentionally limited to `src/algo/rt_pip_custom.cu` in the RayJoin
author program.

It does not change:

- LSI;
- overlay construction;
- output-chain writing;
- CDB parsing;
- dataset conversion;
- timing or reporting semantics.

## Semantic Change

The patch implements the author-clarified deterministic point-location contract:

- when vertical PIP candidates have the same primary hit distance, encode the
  slope-based SoS preference into the distance reported to OptiX;
- `query_map_id == 0` prefers larger normalized slope;
- `query_map_id == 1` prefers smaller normalized slope;
- more preferred candidates report a slightly smaller `t_reported`, so OptiX's
  strict traversal pruning cannot pick an arbitrary equal-`t` candidate.

The patch also aligns the author source's internal equal-height comparator with
the adjacent source comment and the author clarification. The committed source
condition appeared to execute the opposite of its comment; Goal4834 treats the
author clarification as the controlling semantic patch.

## Build Compatibility

This patch contains no CUDA/NVTX/GCC compatibility edits. If a modern POD build
needs compatibility edits, those must remain isolated from this semantic patch
and be reported separately.
