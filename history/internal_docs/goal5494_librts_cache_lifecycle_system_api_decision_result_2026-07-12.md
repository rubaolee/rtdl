# Goal5494 LibRTS Cache Lifecycle System-API Decision

## Status

```text
cache_lifecycle_decision__keep_app_owned__system_api_promotion_fail_closed
```

## Decision

Do not promote the Goal5491 `.npz`/JSON cache lifecycle into RTDL core at this
time. The cache is useful and correctly hash-bound, but the only consumer is
the LibRTS paper app. The cache also encodes app-owned WKT-to-MBR derivation
and exact-input provenance policy.

The existing generic system boundary is sufficient:

```text
app WKT or cache -> validated Aabb2DColumns -> RTDL AABB prepare/query
```

A future system cache API requires a second non-LibRTS consumer, a generic
cache lifecycle contract independent of WKT/paper identity, and a separate
review gate. Until then, the cache remains app-owned and is not counted as a
new RTDL core primitive.

## Evidence

- Goal5487 generic `Aabb2DColumns` has a non-app synthetic consumer.
- Goal5491 exact cache reuse matches `103189` on `lakes.bz2`.
- No second application currently consumes the cache lifecycle.

## Claim boundary

No performance ratio, full paper claim, Figure 6 claim, device zero-copy claim,
or Embree evidence is authorized by this decision.
