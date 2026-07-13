# Call For Review: Goal5494 LibRTS Cache Lifecycle System-API Decision

Please review whether Goal5491's exact AABB cache should become an RTDL system
API. The proposed decision is fail-closed: keep the WKT-derived cache
app-owned until a second non-LibRTS consumer and a generic lifecycle contract
exist.

Questions:

1. Is the current `Aabb2DColumns` boundary sufficient without a core cache API?
2. Does the cache's WKT/provenance policy make immediate core promotion
   app-shaped?
3. Is requiring a second non-LibRTS consumer a sufficient promotion gate?
4. Does the decision preserve all no-ratio/no-Figure/no-zero-copy/Embree
   boundaries?

Expected shape:

```text
Verdict: approve | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
```
