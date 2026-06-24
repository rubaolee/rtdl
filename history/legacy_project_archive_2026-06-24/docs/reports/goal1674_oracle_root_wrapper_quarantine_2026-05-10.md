# Goal1674 Oracle Root Wrapper Quarantine

Date: 2026-05-10

Status: local source cleanup for the app-agnostic native-engine track.

## Verdict

The single `legacy_oracle_wrapper` item from Goal1672 has been removed from the
strict native leakage symbol set.

The root oracle aggregator no longer includes:

```text
oracle/rtdl_oracle_polygon.cpp
```

It now includes the neutral implementation chunk:

```text
oracle/rtdl_oracle_geometry_cells.cpp
```

This is a filename/include quarantine only. It does not remove polygon or
Jaccard app semantics from the oracle API implementation, and it does not
authorize any app-agnostic native-engine claim.

## Current Local Audit Result

After Goal1673 and Goal1674:

- no `pose`-named OptiX native symbols remain;
- the `rtdl_oracle_polygon` root-wrapper symbol is absent;
- the strict dirty native symbol count is `99` with known regex false positives
  from uppercase `RTDL_DB_*` constants;
- remaining real app-shaped native surfaces still include database, graph,
  polygon/GIS, KNN, Hausdorff, and Jaccard families.

No pod validation was run.
