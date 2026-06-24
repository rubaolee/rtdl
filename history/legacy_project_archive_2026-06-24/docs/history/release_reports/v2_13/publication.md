# RTDL v2.13 Publication Note

Status: published source-tree publication packet.

Date: 2026-06-13

Version marker: `v2.13`

## Post-Publication Bridge Note

Goal4378 preserves v2.13 as the already-created source-tree release marker and
opens v2.14 as the next formal cleanup and benchmark-app boost release target.
v2.14 has since been published, so this file is preserved as previous-release evidence rather than the current source-tree release note.

This bridge note adds one important RayJoin caveat after Goal4376: near author
process wall is not author hot-compute parity. v2.13 must not be used to claim
that RTDL's generic hot path matches the RayJoin authors' specialized
C++/CUDA/OptiX hot path.

## Published Statement

RTDL v2.13 is a previous source-tree release for the refreshed row-scoped NVIDIA OptiX/RT-core versus Embree CPU comparison. The release keeps every published performance sentence tied to a benchmark row, contract, direction, and caveat; the current release is v2.14.

## Public Wording That Is Allowed

```text
RTDL v2.13 has row-scoped evidence that selected prepared OptiX/RT-core paths can outperform same-contract or explicitly caveated Embree CPU baselines across the promoted benchmark suite. Each published sentence must name the benchmark row, contract, speedup direction, and caveat.
```

PIP wording must include the mixed-row distinction:

```text
Spatial RayJoin PIP is not a broad RT-core win in v2.13. The refreshed human-scale public CDB slice is near parity and slightly Embree-faster; the stricter Goal4368 full same-stream exact executor is an OptiX-over-Embree engineering win but still slower than RayJoin RT.
```

## Public Wording That Is Blocked

- Do not say RT cores make every benchmark app faster.
- Do not say these are whole-application speedups.
- Do not say RTDL reproduces the RayJoin paper.
- Do not say RTDL beats RayJoin as a whole system.
- Do not say RTDL hot compute matches the RayJoin authors' specialized
  C++/CUDA/OptiX hot path.
- Do not say RTNN is an RT-core neighbor-search speedup.
- Do not say partner selection is automatic or universally Numba-based.
- Do not say Intel GPU or AMD GPU performance is covered by this packet.

## Validation Summary

- Refreshed human-scale packet: pass with all rows in the 1-10s aggregate band.
- Embree CPU fairness packet: pass with threads=8 reference, zero fallbacks, and zero RT-core-accelerated Embree rows.
- Public wording packet: pass with zero unexplained rows.
- Goal4368 PIP exact executor: pass; exact counts match and RayJoin RT remains faster than RTDL PIP.

## Publication Boundary

This publication packet authorizes bounded row-scoped wording only.

Validation status: `accept`.
