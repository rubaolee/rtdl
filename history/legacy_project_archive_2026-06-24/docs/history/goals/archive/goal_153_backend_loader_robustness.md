# Goal 153: Backend Loader Robustness

## Why

Real user-style testing exposed a robustness gap:

- a stale backend shared library can surface as a raw undefined-symbol or
  `AttributeError` failure

Even when the current source already contains the expected symbol, that is
still a product problem because the user experience is a confusing backend
crash instead of a clear rebuild/ABI-drift diagnostic.

## Scope

- harden backend shared-library loading so missing exports fail with clear RTDL
  diagnostics
- add regression coverage for stale Vulkan/OptiX shared libraries
- add missing Vulkan runtime coverage for `segment_polygon_anyhit_rows`
- record the difference between:
  - current source-level backend surface
  - stale built-library drift on a user machine

## Acceptance

- Vulkan loader reports missing exports with a clear rebuild hint
- OptiX loader reports missing exports with a clear rebuild hint
- Vulkan test coverage includes `segment_polygon_anyhit_rows`
- focused robustness tests pass locally
- the report states clearly that the Antigravity symbol error was treated as a
  real user robustness problem, not dismissed as “not our issue”
