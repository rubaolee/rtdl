# Goal4854: Section 5.3 PIP Contract Extraction Plan

Date: 2026-07-01

## Purpose

Start RayJoin paper Section 5.3 reproduction work without repeating the earlier failure mode of blind POD runs.

Section 5.3 is **PIP Performance**. The paper states that PIP is RT-favorable because only the closest hit needs to be found, enabling RayJoin to use the ray-tracing ClosestHit shader rather than traversing all geometries. Table 3 reports PIP processing/preprocessing timings for the same eight dataset pairs used in Section 5.2.

This goal is a planning and contract-extraction goal only. It does not authorize a performance run yet.

## Required Inputs

1. RayJoin paper Section 5.3 and Table 3.
2. Author source code for PIP.
3. AuthorPatch baseline definition used in the current project line.
4. Current RTDL public primitives and Numba partner surface.
5. Prior RTDL bundled-helper evidence, classified as bundled-helper evidence only.

## Work Items

### A. Extract the paper contract

Record:

- What exactly the Section 5.3 PIP workload counts or returns.
- Which eight dataset pairs are used.
- Which reported table numbers correspond to RayJoin processing time and preprocessing time.
- What correctness oracle the author uses for PIP.
- Whether the workload is count-only, face-id returning, inside/outside returning, or a richer point-location result.

### B. Read the author source path

Identify the author functions and command-line shape used for Section 5.3 PIP. Record:

- Input CDB roles.
- Query direction.
- Closest-hit/tie-breaking behavior.
- Precision/conservative representation behavior.
- Whether author code uses raw PIP, point-location, or a higher-level helper.

### C. Map RTDL public capabilities

Classify each required stage as exactly one of:

- `public_generic_rtdl_primitive`
- `numba_user_continuation`
- `public_python_app_logic`
- `bundled_rayjoin_helper`
- `missing_released_capability`
- `authorpatch_baseline_only`

The mapping must not hide a RayJoin bundled helper behind generic language wording.

### D. Select the first correctness gate

Choose the smallest decisive pair or synthetic CDB-like case that can prove the PIP contract before performance.

The preferred first gate should be:

- Cheap enough to rerun repeatedly.
- Able to expose closest-hit / tie-break / boundary behavior.
- Comparable against AuthorPatch output.
- Implemented through public RTDL primitive(s) and Numba only if Numba is truly user-level app code.

### E. Decide the next executable goal

After A-D, write the next executable goal. It must say whether Section 5.3 can proceed as:

- `public_generic_rtdl_pip_route_available`
- `bundled_helper_only_route_available`
- `blocked_by_missing_public_pip_capability`
- `blocked_by_authorpatch_or_input_gap`

## Verification Standard

Goal4854 passes only if it produces a written contract map with:

- Paper citations or extracted line references.
- Author source symbol/function references.
- RTDL public API references.
- Explicit bundled-helper separation.
- A concrete next correctness gate.

## Non-Authorization

This goal does not authorize:

- Any Section 5.3 performance claim.
- Any full eight-pair Section 5.3 claim.
- Any Section 5.7 overlay claim.
- Treating bundled RayJoin helper behavior as generic RTDL language evidence.
- Public release tagging.
- V3/V4 resurrection.

## Exit Label

`section53_pip_contract_extraction_plan_ready`
