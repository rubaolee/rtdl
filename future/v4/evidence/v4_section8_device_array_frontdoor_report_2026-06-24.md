# V4 Section 8 Device-Array Front-Door Evidence Report

Date: 2026-06-24
Status: evidence report; not a V4 release authorization

## Verdict

The V4 fixed-radius count-threshold primitive now has a measured GPU
device-array front door on the RTX pod. The route uses the
`rtdsl.v4_fixed_radius` wrapper, accepts caller-owned Torch CUDA columns,
prepares the OptiX scene once, reuses device output columns, and keeps Python
point objects and app row materialization out of the timed hot path.

This clears the product-boundary blocker identified by Route D for this
primitive. The earlier Python-facing prepared summary route was 452x to 1140x
slower than the independent Route D row baseline. The new Torch device-array
front door shrinks that gap by 1023x to 9699x across the serious sizes.

This report does not authorize V4 release or broad V4 speedup wording. It
supports a narrower internal claim: for the fixed-radius count-threshold
contract, the GPU-resident device-array product route now reaches the same
performance class as the independent hand-written OptiX row ceiling under the
measured boundary.

## Files

- Harness: `scripts/v4_section8_device_array_frontdoor_validation.py`
- API wrapper: `src/rtdsl/v4_fixed_radius.py`
- Test: `tests/v4_section8_device_array_frontdoor_validation_test.py`
- API test: `tests/v4_fixed_radius_device_array_api_test.py`
- User example: `future/v4/examples/fixed_radius_torch_device_arrays.py`
- Example evidence: `future/v4/evidence/v4_fixed_radius_torch_device_arrays_example_result_2026-06-24.json`
- Serious evidence: `future/v4/evidence/v4_section8_device_array_frontdoor_result_2026-06-24.json`
- Smoke evidence: `future/v4/evidence/v4_section8_device_array_frontdoor_smoke_result_2026-06-24.json`
- Route D ceiling: `future/v4/evidence/v4_section8_route_d_result_2026-06-24.json`
- Prior prepared summary baseline: `future/v4/evidence/v4_section8_prepared_hot_path_result_2026-06-24.json`

## Timing Boundary

Included in timed repeats:

- prepared RTDL device-column query
- native OptiX fixed-radius count-threshold launch
- synchronization before return
- writes into reused caller-owned Torch CUDA output columns

Excluded from timed repeats:

- fixture construction
- Torch device-array construction
- prepared scene construction
- correctness host reductions
- app-level Python density-row conversion

Hot-path exclusions are intentional: this route is the V4 Python GPU ecosystem
front door, where users already hold arrays or tensors. It is not a Python
`Point` row app route.

The measured partner is Torch CUDA tensors. The harness has a CuPy mode, but
CuPy was not installed on the measured pod, so this report does not claim CuPy
performance or CuPy product readiness.

## Correctness

All serious sizes passed:

| copies | points | threshold reached | outliers | neighbor count sum | correctness |
|---:|---:|---:|---:|---:|:---:|
| 8,192 | 65,536 | 49,152 | 16,384 | 163,840 | pass |
| 32,768 | 262,144 | 196,608 | 65,536 | 655,360 | pass |
| 131,072 | 1,048,576 | 786,432 | 262,144 | 2,621,440 | pass |

## Timing Summary

| copies | points | device-array median | prior summary median | Route D rows median | prior summary / Route D rows | device-array / Route D rows | gap reduction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8,192 | 65,536 | 0.000278s | 0.284516s | 0.000629s | 452.35x | 0.44x | 1022.93x |
| 32,768 | 262,144 | 0.000311s | 1.193533s | 0.001542s | 774.10x | 0.20x | 3841.66x |
| 131,072 | 1,048,576 | 0.000546s | 5.290915s | 0.004641s | 1140.11x | 0.12x | 9699.17x |

The device-array route is faster than the Route D row baseline under this
specific boundary because Route D deliberately includes host query upload and
host result download in its measured row route. The V4 front door measures the
GPU-resident product contract: input columns are already on device and output
columns remain on device. This is a valid V4 user route, but it is not a pure
kernel-to-kernel comparison.

The first measured size reported a much larger `prepare_sec` than the later
sizes. That is consistent with CUDA context creation and OptiX module/library
initialization on the first prepared call; prepare time is outside the timed hot
path above. Later steady-state prepares were in the 2-5 ms range for the larger
fixtures.

## Gate Result

The predeclared product-boundary gate passed:

- required at least 10x gap reduction over the prior Python-facing prepared
  summary route
- required device-array to Route D row gap at or below 100x
- required at least 2 serious sizes to pass
- actual result: all 3 serious sizes passed

## Interpretation

Route D showed that the RT-core primitive itself was fast and that the old
product path was dominated by Python object packing, FFI/result conversion, and
app-row materialization. This experiment removes that boundary for one real
V4-style product route:

- caller supplies Torch CUDA point columns
- the V4 wrapper prepares a generic OptiX fixed-radius scene
- the V4 wrapper runs the fused count-threshold continuation
- output columns are reused and remain on device
- no Python point rows or app density rows are in the timed path

The JSON metadata uses `true_zero_copy_authorized` for the caller-supplied
columns and output columns: those buffers avoid host staging in the hot path.
It also discloses internal device-resident AABB/BVH staging inside the native
route. Those two facts are compatible: zero-copy here means no host round-trip
for the user-facing array handoff, not absence of native device workspace.

This is the first strong evidence that the V4 architecture should continue:
Tier 2 fused native primitives plus a GPU-array front door can move the product
path into the native performance class.

## Authorized Internal Claim

Pending external review, this evidence can support:

> For the fixed-radius count-threshold contract on the measured RTX pod, RTDL's
> Torch device-array front door runs correctly with no Python point-row hot-path
> boundary and reduces the prior Python-facing product-boundary gap to Route D
> by over 1000x on all serious sizes.

## Unauthorized Claims

This report does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier 3 callback/PTX claims
- app-specific native engine claims
- claims that every future primitive will match this result
- claims that the old Python point-row app route is now fast

## Next Engineering Target

After external review, continue V4 by hardening this route as the canonical
fixed-radius V4 public primitive surface:

1. Keep `rtdsl.v4_fixed_radius` as the first fixed-radius V4 wrapper surface,
   with Torch as the measured first partner and CuPy gated until measured.
2. Add user-facing V4 documentation and a minimal Torch tensor example after
   external review accepts the wrapper evidence.
3. Add a second Tier 2 primitive only after this fixed-radius front door is
   documented, tested, and review-accepted.
4. Keep Tier 3 callback support as a spike, not a V4.0 release gate.
