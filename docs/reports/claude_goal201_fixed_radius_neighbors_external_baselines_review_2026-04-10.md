# Claude Review: Goal 201 Fixed-Radius Neighbors External Baselines

Date: 2026-04-10

## Verdict

Goal 201 is complete and honest. All five acceptance criteria are met. Close it for `v0.4`.

## Findings

**Correctness.**
The SciPy baseline correctly re-applies every RTDL contract step after
`query_ball_point`: explicit `distance <= radius` re-filter via `math.hypot`,
per-query sort by `(distance, neighbor_id)`, `k_max` truncation after ordering,
then a final global sort by `query_id`. The library return order is never
trusted as the contract. The PostGIS SQL matches exactly: `ST_DWithin` as a
candidate predicate, `ROW_NUMBER() OVER (PARTITION BY q.id ORDER BY
ST_Distance(...), s.id)` for deterministic `k_max` truncation, and a final
`ORDER BY query_id, distance, neighbor_id`. SRID=0 (planar) geometry is the
right choice for a Euclidean workload. The `_FakeKDTree` in the test file uses
squared-distance comparison correctly (`<= radius_sq`), so the authored-case
parity assertions are sound.

One minor observation: the `query_table` / `search_table` names in
`build_postgis_fixed_radius_neighbors_sql` are interpolated via f-string rather
than parameterized. These are internal defaults, not user-supplied strings, so
this is acceptable for a bounded comparison helper, but worth noting if the
function is ever exposed more broadly.

**Contract honesty.**
Neither baseline silently inherits library semantics. Both explicitly reconstruct
the RTDL output shape. The runner correctly pairs each external backend against
the Python truth path for parity comparison, not against the Embree path, which
is the right reference.

**Optional-dependency honesty.**
`scipy_available()` and `postgis_available()` use `importlib.util.find_spec`
with no import-time side effects. Error messages clearly name the missing
dependency and the install action. The README Limitations section states
explicitly that SciPy and PostGIS are optional comparison dependencies, not
required first-run dependencies. No test requires either library to be present;
the test suite uses `_FakeKDTree` and `_FakePostgisConnection` throughout.

**Scope.**
Goal 201 does not claim performance wins, does not touch the public workload
contract, and does not introduce OptiX or Vulkan work. The external baseline
role is correctly bounded to moderate comparison and SQL-backed validation.
Test coverage spans authored, Natural Earth, runner integration, and SQL shape
assertions. The baseline runner CLI `--backend scipy` and `--backend postgis`
are wired and guarded.

## Summary

Goal 201 cleanly adds the first external comparison story for
`fixed_radius_neighbors` without letting either SciPy or PostGIS define the
workload contract. The RTDL truth path remains the Python reference and native
CPU/oracle. All acceptance criteria check out. The implementation is minimal,
honest about optionality, and correctly scoped for `v0.4`.
