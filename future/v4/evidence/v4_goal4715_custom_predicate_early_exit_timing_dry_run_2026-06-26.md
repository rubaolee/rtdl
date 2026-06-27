# V4 Goal4715 Custom Predicate Early-Exit Timing

- status: `dry_run_contract_passed`
- classification: `None`
- primary geomean V3 speedup: `None`
- min primary V3 speedup: `None`

| scale | regime | role | ok | V4 s | fallback s | fallback/V4 | V4 invocations | fallback invocations |
|---:|---|---|---|---:|---:|---:|---:|---:|

## Boundary

This gate compares V4 any-hit predicate early termination against a materialized-device fallback that traces the same geometry, writes all hit layers to device memory, then evaluates the predicate and reduces accepted flags in separate device kernels. It does not authorize release, public Tier-3 support, arbitrary callback support, raw OptiX callback support, or all-app claims.
