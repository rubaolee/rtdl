# Claude Review — Goal 201 Fixed-Radius Neighbors External Baselines
## 2026-04-10

## Verdict

Goal 201 is closed and clean. All five acceptance criteria are met. The SciPy
and PostGIS baselines are correct, the contract is faithfully re-applied in both
paths, optional-dependency handling is honest throughout, and the scope is
exactly right for `v0.4`.

## Findings

**Contract correctness — SciPy path.**
`run_scipy_fixed_radius_neighbors` calls `query_ball_point(r=radius)` for
candidate generation, then re-applies `distance <= radius` via `math.hypot`
before sorting. The secondary check is not redundant noise: it makes the
inclusive-boundary rule explicit and guards against any future tree-factory
substitution whose radius semantics differ. The per-query sort is
`(distance, neighbor_id)`, truncation to `k_max` comes after that sort, and the
final global sort is by `query_id`. This is the exact public contract.

**Contract correctness — PostGIS path.**
The SQL uses `ST_DWithin` (inclusive) as the candidate predicate, `ROW_NUMBER()
OVER (PARTITION BY q.id ORDER BY ST_Distance(...), s.id)` for deterministic
top-`k` ranking, and `ORDER BY query_id, distance, neighbor_id` in the outer
query. The geometry column is typed `geometry(Point, 0)` with SRID 0, which is
appropriate for the Euclidean contract. Parameters are passed via `%s`
placeholders throughout — no injection surface. One note: `query_table` and
`search_table` are interpolated via f-string rather than parameterized; they are
internal defaults with no user-supplied path, so this is acceptable for a
bounded comparison helper.

**Optional-dependency honesty.**
`scipy_available()` and `postgis_available()` use `importlib.util.find_spec`
rather than a bare import, so availability checks are free of import-time side
effects. `connect_postgis` raises with a clear message if neither a DSN argument
nor `RTDL_POSTGIS_DSN` is set, and raises separately if `psycopg2` is absent.
The README Limitations section states the optional-dependency contract in plain
language. Nothing in the normal first-run path touches either import.

**Test coverage.**
Seven tests cover: authored-case parity (SciPy and PostGIS), global sort
ordering on reversed query-id input, SQL shape assertions, runner-level parity
for both backends via mocks, and the public Natural Earth fixture through the
fake tree. The `_FakeKDTree` and `_FakePostgisConnection` fakes are
behaviorally correct: `_FakeKDTree.query_ball_point` uses `distance² <= radius²`
(equivalent to `distance <= radius`), and the fake cursor replicates the
deterministic sort the real PostGIS SQL would produce.

**Scope.**
No performance claims, no changes to the public workload contract, no new
required dependencies, no OptiX or Vulkan work. The goal document, progress
report, and code are in agreement on all of this.

## Summary

Goal 201 adds a correct, honestly-scoped external comparison story to
`fixed_radius_neighbors` without touching the public contract or the first-run
dependency set. Both baselines re-apply RTDL semantics rather than adopting
the external library's native output ordering as truth. The optional-dependency
wiring is clean in code and stated plainly in docs. `v0.4` now has a full
stack for this workload: Python truth path, native CPU/oracle, Embree, SciPy
baseline, and bounded PostGIS comparison helper.
