# Goal 85 Report: Vulkan Hardware Validation And Measurement

Date: 2026-04-04

## Summary

Goal 85 closes the first real hardware-backed validation loop for the Goal 78
Vulkan positive-hit sparse redesign.

What is now established:

- the revised Vulkan backend runs correctly on the Linux GPU host
- the broader Vulkan goal51 validation ladder is parity-clean on hardware
- the new positive-hit Vulkan tests in `tests.rtdsl_vulkan_test` run and pass on
  hardware
- a bounded exact-source prepared county/zipcode CDB slice is parity-clean and
  shows that Vulkan is no longer the old catastrophic Goal 72 path

What is **not** established:

- Vulkan does **not** yet join the OptiX/Embree long exact-source prepared
  closure
- on the exact long surface used by Goals 82 and 83, Vulkan still fails before
  execution because the sparse candidate buffer keeps the old worst-case
  `point_count x poly_count` allocation contract and trips the current
  `512 MiB` Vulkan output guardrail

## Host

- host: `lestat-lx1`
- GPU host family already used for accepted OptiX / Embree closure rounds

## Validation Performed

### 1. Focused Vulkan unit suite

Linux command:

```bash
cd /home/lestat/work/rtdl_goal85
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test tests.goal85_vulkan_prepared_exact_source_county_test
```

Result:

- `20` tests
- `OK`

Important meaning:

- the 5 Goal 78 positive-hit Vulkan tests that were previously skipped on the
  Mac now executed on real hardware and passed

### 2. Goal 51 Vulkan validation ladder

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_smoke_artifacts_2026-04-04/goal51_summary.json`

Result:

- `8 / 8` targets parity-clean
- Vulkan version:
  - `0.1.0`

Representative warm runtimes:

- authored `lsi`: `0.517637768 s`
- authored `pip`: `0.315956886 s`
- derived tiled `pip`: `0.013240372 s`

This establishes that the revised Vulkan runtime is not just compiling. It is
executing the accepted validation ladder correctly on hardware.

## Bounded Prepared Measurement

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_prepared_exact_source_artifacts_2026-04-04/summary.json`

This bounded exact-source CDB surface produced:

- row count: `7863`
- parity preserved on both reruns: `true`
- run 1:
  - Vulkan: `0.858198020 s`
  - PostGIS: `0.393232202 s`
- run 2:
  - Vulkan: `0.333589648 s`
  - PostGIS: `0.400314831 s`

Interpretation:

- Vulkan is parity-clean
- Vulkan can beat PostGIS on a rerun of this bounded prepared surface
- but this is not the same long exact-source surface used by the accepted OptiX
  and Embree long-workload closures

## Exact Long Surface Attempt

Goal 85 also attempted the same long exact-source prepared county/zipcode
surface used by the accepted OptiX and Embree packages:

- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

Result:

- Vulkan did **not** produce a timed row
- runtime failed before execution with:

```text
RuntimeError: Vulkan PIP positive-hit output exceeds current Vulkan guardrail of 536870912 bytes
```

Meaning:

- Goal 78 fixed the old host-side `O(P x Q)` exact-finalize waste
- but the current sparse-candidate implementation still preallocates for the
  worst-case candidate count
- so the long exact-source surface remains blocked by the same underlying
  allocation contract

## Accepted Claim

Goal 85 establishes:

1. Goal 78 is now hardware-validated as a working Vulkan implementation.
2. The Vulkan positive-hit redesign is parity-clean on the accepted Vulkan
   validation ladder.
3. Vulkan is materially improved on a bounded prepared exact-source CDB slice.
4. Vulkan is **still blocked** from joining the accepted long exact-source
   prepared comparison row because of worst-case candidate allocation.

## Non-Claims

- Goal 85 does not claim that Vulkan beats PostGIS on the long exact-source
  county/zipcode surface used by OptiX and Embree.
- Goal 85 does not claim that Vulkan is now generally competitive with the two
  mature backends.
- Goal 85 does not claim that the allocation/scaling problem is solved.

## Conclusion

Goal 85 is a real step forward for Vulkan:

- the redesign is validated on hardware
- parity is clean on the accepted smoke ladder
- the backend is no longer just a redesign on paper

But it also sharpens the remaining Vulkan problem:

- the backend is now blocked primarily by worst-case sparse-candidate allocation
  on the true long exact-source surface, not by basic correctness of the new
  positive-hit execution path.
