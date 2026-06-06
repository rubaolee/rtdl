# Goal3598 - v2.9 RayJoin Performance-First Addendum

Date: 2026-06-06

Status: v2.9 internal progress addendum; not release or public speedup authorization.

## Purpose

Goal3537/Goal3541 closed v2.8 internally and opened v2.9 as a performance-first lane. The most important RayJoin instruction in Goal3538 was:

> replace a single noisy partial RayJoin number with promoted-contract and larger resident/repeat evidence.

Goals3589-3596 now answer the first RayJoin slice of that instruction.

## What Changed After The v2.8 Closeout

| Goal | Role | Reading |
| --- | --- | --- |
| Goal3589 | Same-contract CuPy-vs-RTDL/OptiX baseline on authored fixtures | Negative pressure test: CuPy beats the current simple PIP/overlay authored fixtures; LSI only becomes RTDL/OptiX-favorable at stress scale. |
| Goal3592 | Explicit mixed-route packet | Route choice must be explicit and contract-specific; no automatic dispatcher. |
| Goal3593 | Bounded public-CDB same-contract probe | Public CDB changes the route picture: PIP remains CuPy-favorable, but LSI and overlay strongly favor RTDL/OptiX. |
| Goal3594 | Gemini review of Goal3593 | `accept-with-boundary`; flags artifact git cleanliness before larger packet inclusion. |
| Goal3595 | Clean-checkout repeat-200 public-CDB stability packet | Addresses cleanliness and longer-timing concerns; overlay CuPy hot loop accumulates about 9.94s, counts match, LSI/overlay remain strongly RTDL/OptiX-favorable. |
| Goal3596 | Public-CDB PIP route audit | Existing switches do not close the PIP gap; exact prepared OptiX is the best RTDL-only scalar count route, but CuPy remains fastest for simple scalar PIP count. |
| Goal3599 | Barnes-Hut resident-repeat packet | Current main has valid app-level resident-repeat evidence for the prepared OptiX node-coverage contract; the old subprocess-repeat row should no longer be treated as silently partial. |
| Goal3601 | LibRTS same-contract resident-repeat packet | v2.3 and current main both run the same prepared OptiX AABB hot loop from clean checkouts; current is a clean parity row at `1.005864x`. |

## Current RayJoin Public-CDB Route Table

| Case | Contract | Recommended v2.9 route for this bounded public-CDB slice | Evidence |
| --- | --- | --- | --- |
| `pip_county512` | PIP positive assignment count | CuPy dense CUDA-core count | Goal3595: CuPy `0.000437917s`, RTDL/OptiX exact prepared count `0.000802434s`, OptiX+CuPy refiner `0.002150856s`. |
| `lsi_county512_soil512` | LSI segment-intersection count | RTDL/OptiX prepared route | Goal3595: CuPy `0.021059401s`, RTDL/OptiX `0.000185231s`, `113.693x` RTDL/OptiX-vs-CuPy. |
| `overlay_county512_soil512` | Overlay active pair-dependency count | RTDL/OptiX prepared route | Goal3595: CuPy `0.049443172s`, RTDL/OptiX `0.000538940s`, `91.742x` RTDL/OptiX-vs-CuPy. |

The Goal3595 geomean across the three bounded public-CDB rows is `12.8536x` RTDL/OptiX-vs-CuPy, but this is not a single RayJoin app headline because PIP intentionally routes to CuPy while LSI/overlay route to RTDL/OptiX. Treat it as contract-level evidence.

## v2.9 Position

This addendum improves the RayJoin part of the v2.9 plan:

- The old "spatial RayJoin prepared full route" partial row is no longer the right evidence unit.
- RayJoin now has a contract-level public-data table with long-repeat stability for the heaviest row.
- The correct v2.9 user story is explicit composition: use RTDL/OptiX where generic RT traversal pays; use CuPy where dense CUDA-core logic is the best simple continuation; keep the route visible.
- The remaining RayJoin runtime gap is not more metadata. It is a generic exact point-in-closed-shape scalar count primitive or boundary-selection primitive that can beat dense CuPy for PIP without app-specific native code.

## What This Does Not Close

Goal3598 does not finish all v2.9 performance work:

- Barnes-Hut node coverage still needs full-table integration, but Goal3599 closes the old silent-partial diagnosis for current main.
- LibRTS AABB index still needs full-table integration, but Goal3601 closes the old same-contract repeat ambiguity and classifies it as near-parity, not a major performance blocker.
- Hausdorff and robot collision repeat/resident hooks still need final positioning in the full v2.9 table.
- A single v2.9 all-benchmark table must still be regenerated with same-contract and promoted-contract views.
- External review is still required before any larger v2.9 performance conclusion.

## Boundary

Goal3598 does not authorize:

- public v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app RayJoin speedup wording;
- RayJoin paper reproduction wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

## Next Engineering Step

For RayJoin specifically, the next high-value work is v2.9 primitive design and implementation for generic exact point-in-closed-shape scalar count or boundary-event selection. It must preserve exact positive-membership semantics on the public county slice where the current filtered fast modes overcount.

For the overall v2.9 plan, Barnes-Hut and LibRTS are no longer the best P0 engineering targets for fresh code. Barnes-Hut now has current-main resident-repeat evidence, and LibRTS is a clean near-parity same-contract row. The next high-value work is either a full v2.9 all-benchmark packet refresh or targeted tuning on rows with material gaps rather than parity-level noise.
