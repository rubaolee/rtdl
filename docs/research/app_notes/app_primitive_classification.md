# RTDL App Primitive Classification

This note classifies the public app examples by the RTDL primitive pattern they
need. It is meant for implementation planning, review, and pod preparation. It
is not a tutorial and does not authorize public speedup, whole-app, broad RTX,
or true zero-copy claims.

## Classification Table

| App | Primary primitive pattern | Current maturity | Python owns | Backend should own | Main risk |
| --- | --- | --- | --- | --- | --- |
| Database analytics | `REDUCE_INT` / `REDUCE_FLOAT` over prepared compact DB traversal | Candidate generic reduction path | Fixture construction, DB policy, presentation | Compact aggregate summaries | Python/interface overhead can dominate; not a DBMS claim |
| Graph analytics | `COUNT_HITS` / visibility traversal summaries | Candidate generic traversal-plus-count path | Graph fixtures, BFS/triangle policy, graph-system semantics | Visibility/ray traversal and selected counts | Broad graph analytics claims are unsafe |
| Service coverage gaps | Fixed-radius `COUNT_HITS` / threshold reduction | Strong reduction candidate | Household/clinic fixtures and service interpretation | Covered/uncovered compact counts | Witness rows are omitted in compact modes |
| Event hotspot screening | Radius self-join `COUNT_HITS` / threshold reduction | Strong reduction candidate | Event fixture and hotspot policy | Hotspot count summaries | Threshold semantics must stay exact |
| Facility KNN assignment | Split path: KNN rows plus fixed-radius coverage reduction | Mixed: row path plus reduction path | Ranked assignment policy, depot loads, fallback choices | Coverage-threshold decision | KNN rows and coverage decisions are different contracts |
| Road hazard screening | Segment/polygon `COUNT_HITS` | Strong reduction candidate | Hazard priority policy and reporting | Segment/polygon hit counts | GIS/routing semantics are outside RTDL |
| Segment/polygon hitcount | Segment/polygon `COUNT_HITS` | Strong generic primitive candidate | Input packing and result display | Per-segment counts | Pair witnesses require a different path |
| Segment/polygon any-hit rows | `ANY_HIT` for flags/counts; `COLLECT_K_BOUNDED` for pair rows | Mixed; bounded collection experimental | Output policy and row interpretation | Flags/counts; bounded pair collection when promoted | Overflow/fail-closed semantics and row completeness |
| Polygon-pair overlap area rows | Candidate discovery plus `REDUCE_FLOAT(SUM)` and `REDUCE_INT(COUNT)` summaries | Candidate generic reduction path after refinement | Polygon fixture/policy and output formatting | Positive candidate discovery and aggregate area/count summaries | Broad overlay claims are unsafe |
| Polygon-set Jaccard | Bounded candidate collection plus area/Jaccard continuation | Blocked on bounded collection promotion | Set construction and similarity policy | Bounded candidate discovery when safe | `COLLECT_K_BOUNDED` stability and overflow handling |
| Hausdorff distance | Fixed-radius `ANY_HIT` threshold decision; min/max distance reductions | Mixed reduction/decision candidate | Exact witness policy and full row output | Threshold decisions and directed summaries | Exact distance rows differ from threshold decisions |
| ANN candidate search | Fixed-radius `ANY_HIT` / threshold reduction | Candidate generic reduction path | ANN ranking, recall policy, index policy | Candidate coverage decisions | Full ANN search is outside RTDL |
| Outlier detection | Radius `COUNT_HITS` / threshold-count reduction | Strong reduction candidate | Label policy and downstream analytics | Density counts and scalar outlier counts | Per-point labels are larger than scalar summaries |
| DBSCAN clustering | Radius `COUNT_HITS` / core threshold reduction | Strong reduction candidate for core counts | Cluster expansion and labels | Core counts/flags | Full clustering is outside RTDL |
| Robot collision screening | Ray/triangle `ANY_HIT` and `COUNT_HITS` | Strong generic primitive candidate | Kinematics, pose generation, planning, visualization | Per-pose flags and hit counts | Witness rows and planning are separate |
| Barnes-Hut force app | Fixed-radius `ANY_HIT` / `COUNT_HITS` candidate coverage | Candidate generic reduction path | Tree policy, opening rule, force reduction | Node-coverage decisions and candidate summaries | Force-vector reduction is not covered by candidate traversal |

## Implementation Groups

### Reduction-First Apps

These apps are the safest near-term generic targets because compact summaries
are semantically natural:

- Service coverage gaps
- Event hotspot screening
- Road hazard screening
- Segment/polygon hitcount
- Outlier detection
- DBSCAN core-count modes
- Robot hit-count and pose-flag modes

The main work is to ensure the native contract is app-name-free and that Python
does not need intermediate row lists for the selected summary mode.

### Split-Contract Apps

These apps expose both row-producing and compact summary/decision modes:

- Facility KNN assignment
- Hausdorff distance
- ANN candidate search
- Barnes-Hut force app

For these apps, the compact mode can become generic earlier than the full row or
ranking mode. Documentation and tests must keep those modes separate.

### Candidate-Refinement Apps

These apps use RTDL for positive candidate discovery plus a refinement or area
continuation:

- Polygon-pair overlap area rows
- Polygon-set Jaccard

They are important, but they are also where claims can become slippery. The
safe wording is candidate discovery and selected compact summaries, not broad
polygon overlay or set-similarity acceleration.

### Bounded-Collection Blocked Apps

These apps need stable bounded collection before their row-producing path can be
promoted:

- Segment/polygon any-hit pair rows
- Polygon-set Jaccard rows

The engineering blocker is not just speed. The primitive must provide
fail-closed overflow behavior, exact bounds tests, bounded result buffers,
Embree/OptiX parity where claimed, and accepted measurement evidence.

## Copy And Materialization Implications

Reduction-first apps are the best current way to reduce bulk movement in the
Python+RTDL architecture. They let RTDL return a compact scalar or per-query
summary instead of materializing large hit/candidate rows back into Python.

Bounded-collection apps are necessary when users need witnesses or candidate
rows. They cannot be replaced by reductions without changing semantics. The
right goal is bounded, explicit, fail-closed collection, not pretending those
rows are unnecessary.

Candidate-refinement apps need extra care because traversal is only one stage.
If exact area, Jaccard, ranking, clustering, force reduction, or planning stays
in Python, documentation must say so directly.

Copy reduction is not zero-copy. None of these classifications are true
zero-copy claims. They describe reduced materialization and clearer ownership
boundaries inside Python+RTDL.
