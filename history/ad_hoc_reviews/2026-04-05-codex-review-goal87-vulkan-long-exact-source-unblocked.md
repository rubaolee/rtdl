# Codex Review: Goal 87 Vulkan Long Exact-Source Unblocked

Verdict: APPROVE

## Findings

- The code change in `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`
  matches the Goal 87 objective: it removes the old worst-case
  `point_count x poly_count` candidate allocation from the Vulkan positive-hit
  path and replaces it with a two-pass count/materialize contract.
- The Linux validation is sufficient for this goal:
  - `make build-vulkan`
  - `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test tests.goal85_vulkan_prepared_exact_source_county_test`
  - result: `20` tests, `OK`
- The imported long exact-source artifact is coherent:
  - row count: `39073`
  - parity preserved on both reruns: `true`
  - Vulkan runtime: about `6.14 s`
  - PostGIS runtime: about `3.05-3.26 s`

## Assessment

The package is technically sound and the claim surface is honest.

What Goal 87 proves:

- Vulkan now runs the accepted long exact-source prepared `county_zipcode`
  positive-hit `pip` surface.
- parity is preserved against PostGIS on that surface.
- the old allocation guardrail is no longer the blocking reason.

What Goal 87 does not prove:

- Vulkan does not beat PostGIS on this surface.
- Vulkan does not yet join the mature OptiX/Embree performance closure.

## Recommended Next Step

Keep Vulkan in the supported-backend story, but treat the next Vulkan goal as a
performance optimization goal rather than another correctness/unblocking round.
