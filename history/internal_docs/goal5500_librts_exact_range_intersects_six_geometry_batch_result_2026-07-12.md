# Goal5500 LibRTS Exact Range-Intersects Six-Geometry Batch

## Status

```text
exact_archive_six_geometry_range_intersects_batch_attempted__3_matched__2_count_mismatch__1_author_oom__externally_reviewed__diagnosis_required
```

Goal5500 extends the exact range-intersects line from one geometry and three
query settings to six official archive geometry/query pairs, using the same
`range-intersects_select_0.01_queries_10000` query family:

```text
parks_Europe
parks.bz2
dtl_cnty
lakes.bz2
USACensusBlockGroupBoundaries
USADetailedWaterBodies
```

All twelve WKT members were selected from the verified Zenodo archive in one
quota-safe extraction. The archive is bound to MD5
`89e589f086038f1cd3af9e3ed67da8c8`, and every selected geometry/query member
has a recorded size and SHA-256. The same extracted files were passed to the
pinned author binary and the RTDL columnar OptiX route.

## Result Matrix

| Geometry | Author count | RTDL count | Outcome |
|---|---:|---:|---|
| `parks_Europe` | 216,977,211 | 216,981,002 | count mismatch, RTDL +3,791 |
| `parks.bz2` | CUDA allocation failure | not run | author OOM |
| `dtl_cnty` | 1,570,285 | 1,570,285 | matched |
| `lakes.bz2` | 1,113,229,623 | 1,113,284,318 | count mismatch, RTDL +54,695 |
| `USACensusBlockGroupBoundaries` | 33,404,355 | 33,404,355 | matched |
| `USADetailedWaterBodies` | 55,205,607 | 55,205,607 | matched |

The result is therefore **3/6 matched**, not a six-case exact correctness
matrix. The two count disagreements are same-input disagreements, but they do
not identify their own root cause: the standard author binary exposes counts,
not relation rows. Possible causes include float32 AABB conversion, native
broad-phase padding, diagonal range-intersection semantics, or another
author/RTDL execution-contract difference. No one of these is promoted to a
conclusion by Goal5500.

The `parks.bz2` case failed closed at the author stage with CUDA
`cudaErrorMemoryAllocation` / `std::bad_alloc`. It is an execution-capacity
failure, not a semantic match or mismatch. The batch runner records the case,
input paths, and error rather than dropping it.

## RTDL Route And Phases

The RTDL route is the generic public columnar path:

```python
columns = Aabb2DColumns(...)
prepared = prepare_aabb_index_2d_columns(columns, backend="optix")
count = prepared.count(box_queries=query_columns, operation="range_intersects")
```

Representative measured RTDL phases from the batch are:

```text
parks_Europe                    load 141.394s  prepare 0.507s  query 0.575s
dtl_cnty                       load  27.774s  prepare 0.009s  query 0.041s
lakes.bz2                      load 407.112s  prepare 0.474s  query 0.688s
USACensusBlockGroupBoundaries  load  97.162s  prepare 0.027s  query 0.050s
USADetailedWaterBodies         load  34.762s  prepare 0.033s  query 0.045s
```

The author reports an internal query metric with loading excluded. RTDL
reports WKT/column loading, preparation, prepared-query wall, and primitive
query phases separately. These denominators are not aligned; no performance
ratio is authorized. The numbers do show that the current RTDL front door is
dominated by large WKT ingestion, but this is an engineering observation, not
a paper-performance claim.

## What This Closes

- exact archive provenance for six representative range-intersects pairs;
- one reusable batch extractor and one fail-closed batch runner;
- same-input author/RTDL count agreement for three geometry families at larger
  official inputs;
- explicit evidence for two large-input count disagreements;
- explicit evidence that `parks.bz2` exceeds the current author GPU allocation;
- phase-separated RTDL measurements with no denominator substitution.

## What Remains Open

- the two count mismatches require diagnosis before any broader exact
  range-intersects claim;
- `parks.bz2` needs a separately authorized capacity strategy or remains
  blocked on the current GPU;
- only six of the inventory's 42 exact range-intersects pairs were attempted;
- pairwise relation equality is not established because the author binary emits
  count only;
- Figure 6, full paper reproduction, author performance parity, whole-program
  speedup, device zero-copy, and Embree evidence remain closed.

The next technically meaningful goal is a generic mismatch diagnostic, not a
claim upgrade: use a bounded pair-row/reference probe or equivalent independent
oracle to distinguish parsing/float32/padding/intersection-contract causes,
while keeping the author count-only limitation visible. Any fix must stay in
generic RTDL AABB semantics or the app-owned adapter; no LibRTS-specific core
primitive is authorized.

## Evidence

```text
Paper-reproduction-apps/librts-paper/data/goal5500_range_intersects_representative_cases.json
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_gate.json
Paper-reproduction-apps/librts-paper/results/goal5500/batch3.log
tests/goal5500_librts_exact_range_intersects_batch_tools_test.py
tests/goal5500_librts_exact_range_intersects_batch_result_test.py
```

Goal5500 is implemented and externally reviewed as honest partial evidence. It
must not be summarized as "six exact range-intersects cases matched". The
range-intersects line remains open pending the required mismatch diagnosis.
