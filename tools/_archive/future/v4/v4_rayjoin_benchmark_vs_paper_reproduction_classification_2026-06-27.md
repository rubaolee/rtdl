# RayJoin Line Classification: Benchmark App vs Paper-Reproduction App

Date: 2026-06-27

## Verdict

The RayJoin family belongs to **both** project lines, but not through one single
app surface.

| Surface | Line | Classification |
| --- | --- | --- |
| `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Benchmark apps | **Benchmark app only**. It is RayJoin-style spatial work, but its own claim boundaries repeatedly say it is not full RayJoin paper reproduction. |
| `src/rtdsl/rayjoin_paper_suite.py` plus `scripts/rayjoin_paper_reproduction_suite.py` | Paper-reproduction apps | **Paper-reproduction line**. This is the separate suite intended to align with RayJoin author programs, datasets, tables, and commands. |
| V4 current 10-app matrix `spatial_rayjoin` row | Benchmark apps | **Benchmark/control row only**. Current V4 route binding marks Spatial RayJoin as `no_v4_app_route_blocker`; the matrix used generated grid64 shape-pair input, not the RayJoin paper suite. |

So the precise answer is:

```text
RayJoin as a project family: both.
The current visible spatial_rayjoin benchmark app: benchmark line only.
The RayJoin paper-reproduction app: separate suite, historically v2.x-era, not
the current V4 benchmark row.
```

## Evidence

### 1. Current Benchmark App Explicitly Blocks Paper-Reproduction Claims

The current app file:

`examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

contains repeated claim boundaries such as:

- `full_rayjoin_reproduction: False`
- `rayjoin_paper_reproduction_claim_authorized: False`
- `rtdl_beats_rayjoin_claim_authorized: False`

It also states that:

```text
RayJoin application policy and paper-specific interpretation stay in Python.
```

and similar wording for point-location, segment-intersection, shape-pair, and
overlay-seed routes.

This means the current app is not allowed to present itself as the paper
reproduction app.

### 2. Separate RayJoin Paper Suite Exists

The separate paper suite:

- `src/rtdsl/rayjoin_paper_suite.py`
- `scripts/rayjoin_paper_reproduction_suite.py`

defines:

- RayJoin paper dataset pairs such as County x Zipcode, Block x Water, LKAF x
  PKAF, and continent lake/park pairs;
- paper programs:
  - LSI via `query_exec -query=lsi`;
  - PIP via `query_exec -query=pip`;
  - polygon overlay via `polyover_exec`;
- paper Table 4 values and dataset statistics;
- exact/bounded availability checks.

This is the correct home for the RayJoin paper-reproduction app line.

### 3. Historical v2.x Paper-Facing Work Exists

The historical closure record:

`history/legacy_project_archive_2026-06-24/docs/reports/goal61_rayjoin_bounded_paper_closure_2026-04-03.md`

closed RayJoin as a **bounded paper-facing package**, not a paper-identical
claim. It explicitly excluded:

- paper-identical reproduction;
- nationwide closure;
- full original continent-family coverage;
- full polygon overlay materialization.

It accepted bounded analogues for Figures 13/14, Table 3, Table 4, and Figure
15 under the then-accepted bounded rule.

The later exact-suite artifact:

`history/legacy_project_archive_2026-06-24/docs/reports/goal4374_rayjoin_exact_paper_suite_2026-06-13/manifest.md`

redefined the target more strictly:

```text
Analogue inputs do not count as exact reproduction. Current RTDL overlay seed
rows do not count as polygon overlay.
```

It recorded LSI and PIP as implemented, while exact-input availability remained
blocked when paper-preprocessed CDBs were missing.

The comparison packet:

`history/legacy_project_archive_2026-06-24/docs/reports/goal4374_rayjoin_exact_paper_suite_2026-06-13/rayjoin_county_zipcode_current_comparison_2026-06-14.md`

showed a same-source County x Zipcode comparison against the RayJoin author RT
code, but still kept public wording locked:

- LSI exact/stable against author RT on that source.
- PIP has an author-shaped device-output route, but RTDL remained much slower
  than the author's RT path.
- Overlay was staged and faster than Embree, but full exact polygon-overlay
  reproduction versus author code was not claimable because of map0 tie
  nondeterminism and output-materialization boundary issues.

The v2.13/v2.14 authors-code packet:

`src/rtdsl/v2_13_rayjoin_authors_code_packet.py`

also says:

- same-query-stream with RayJoin `query_exec`: true;
- scalar-count contract only: true;
- full RayJoin paper reproduction: false;
- public RTDL-beats-RayJoin wording: false.

## Current V4 Matrix Is Not The Paper Suite

The current V4 route binding:

`src/rtdsl/v4_app_route_binding.py`

marks:

```text
spatial_rayjoin -> no_v4_app_route_blocker
```

and records:

- `route_actually_uses_v4_code=False`
- `full_app_route_bound=False`
- `dry_run_possible=False`

The current V4 benchmark summary:

`docs/app_level_benchmark_summary.md`

says the Spatial RayJoin row uses generated grid64 shape-pair input and is a
serious parity/control row, not a speed win.

Therefore the V4 10-app matrix Spatial RayJoin row is not the RayJoin
paper-reproduction app.

## Practical Interpretation

There are two legitimate RayJoin workstreams:

1. **Benchmark app line**
   - Purpose: keep a RayJoin-style spatial benchmark in the RTDL 10-app matrix.
   - Current status: three-version V2.14/V3.0.2/V4.0 generated shape-pair
     matrix exists; result is parity/control, not V4 high-performance evidence.

2. **Paper-reproduction app line**
   - Purpose: reproduce RayJoin paper programs and author-code behavior.
   - Current status: v2.x-era paper-facing assets exist. They include bounded
     closure, same-query-stream authors-code comparison, and a later exact-suite
     scaffold. LSI/PIP are substantially implemented; full public exact
     reproduction remains claim-limited by exact dataset availability,
     author-performance gap on PIP, and overlay exactness/materialization
     boundaries.

## Recommended Next Step

Do not merge these lines silently.

If the project wants a V4 paper-reproduction app line analogous to the new
RT-BarnesHut line, create a new promoted item:

```text
paper_reproduction/rayjoin
```

with its own contract:

- author source and binary;
- exact paper datasets or clearly labeled same-source substitute;
- LSI/PIP/overlay separated;
- correctness parity per program;
- phase and timing basis;
- explicit claim boundary for bounded vs exact reproduction.

Then compare V2.14/V3.0.2/V4.0 under that paper suite separately from the
10-app benchmark matrix.
