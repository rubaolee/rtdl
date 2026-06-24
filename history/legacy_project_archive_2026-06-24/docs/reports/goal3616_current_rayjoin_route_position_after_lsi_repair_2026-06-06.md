# Goal3616 - Current RayJoin Route Position After LSI Repair

Date: 2026-06-06

Status: internal v2.9 route-positioning note. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Current Recommended Route

After Goal3613, the current v2.9 RayJoin public-CDB reference route is:

| Contract | Current Route | Why |
| --- | --- | --- |
| PIP scalar count | CuPy dense CUDA-core count | Goal3604/Goal3606 showed the current RT boundary-signal route is slow and not robust; CuPy remains fastest for this scalar-count contract. |
| LSI count | RTDL/OptiX left-id dense count with strict segment predicate | Goal3613 repaired the previous 4096 mismatch; the route now matches CuPy at 4096 and gives a 2032.908x LSI speedup in the measured artifact. |
| Overlay active-count | RTDL/OptiX prepared shape-pair active count | The RT route remains exact for the measured 4096 slice and gives a 27.704x overlay speedup in the measured artifact. |

## Current Single RayJoin Number

For the measured 4096 public-CDB slice, using an unweighted sum of hot median seconds across PIP, LSI, and overlay_seed:

| All-CuPy Sum Median Sec | Current Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | --- |
| 1.436104300 | 0.007598563 | 188.997x | true |

This is the clearest current internal RayJoin benchmark-app number.

## How To Read Older Goal Notes

Goal3608 and Goal3609 were correct at the time: they identified the mixed-route direction but found that the first 4096 composite failed because the LSI left-id dense count route counted conservative candidates.

Goal3612 provided a safe same-contract fallback by switching LSI to exact prepared RTDL/OptiX count with host double refinement.

Goal3613 then repaired the fast dense-count route itself. Therefore the current route no longer needs the Goal3612 host-refined LSI fallback for this measured 4096 public-CDB slice.

## Remaining Risk

The repaired dense-count route uses the strict float-side segment predicate in the OptiX any-hit program. It matches the current CuPy dense baseline on the measured 4096 public-CDB slice, but broader public claims still need:

- more dataset diversity;
- a documented segment-pair count tolerance policy;
- explicit handling for collinear/endpoint/near-zero-length cases;
- external review of the Goal3612/Goal3613 repair packet;
- a final release/claim packet if the user wants public wording.

## Boundary

This note is for internal route clarity only. It is not a release packet and not a public claim packet.
