# Goal5830 — Public V4 stable-sort demo and concrete CP002 value result

Date: 2026-08-30  
Status: **complete at bounded functional-demo scope**  
External review: **not requested**

## Bottom line

The sorting demo is now real code, not a slide or a host-side simulation.
Application code maps a stable total order to the existing public V4
custom-AABB bounded-relation family, executes the relation through OptiX,
derives ranks from the returned predecessor rows, and linearly scatters the
records.  Goal5830 changed no RTDL core or native source for sorting.

The main input is:

```python
values = (2, 1, 2, 0)
```

The exact result is:

```text
stable order codes:  (10, 6, 12, 3)
RT predecessor rows: ((0,0),(0,1),(0,3),
                      (1,1),(1,3),
                      (2,0),(2,1),(2,2),(2,3),
                      (3,3))
ranks by item id:    (2, 1, 3, 0)
stable records:      ((0,3),(1,1),(2,0),(2,2))
```

The public implementation is
`examples/current/v4_public_stable_sort.py` at
`53cd19d6...35fb`.

## What the code does

### 1. Encode the stable order without computing ranks on the host

For input record `i`:

```python
u_i = (value_i - min(values)) * (n + 1) + i
```

The original item index is the stable tie break.  The host computes this
monotone coordinate only; it does not sort records or compute rank.

The two AABBs are:

```python
indexed_j = [u_j, 0, upper,      1, item_id=j]
source_i  = [u_i, 0, u_i + 0.25, 1, item_id=i]
```

With minimum overlap `0.25`, the boxes overlap exactly when:

```text
(value_j, j) <= (value_i, i)
```

Thus the RT result is a complete predecessor relation.

### 2. Execute through the public RTDL lifecycle

The application uses only `rtdsl.v4`:

```python
verified = compile_protocol_program(
    protocol,
    physical_plan=standard_protocol_physical_plan(protocol),
    any_hit_proof=proof,
)
materialized = verified.materialize(target=target, toolchain=toolchain)
prepared = materialized.prepare(BoundedRelationStaticInput(indexed_boxes))
result = prepared.execute(BoundedRelationBatch(source_boxes))
```

No expected relation rows or Python sorting oracle enter `execute`.

### 3. Convert the RT relation to a stable order

For each item, application code requires exactly one self relation using the
**nominal item ID**, removes it, and counts the remaining predecessors:

```python
rank_i = sum(predecessor_id != item_id for predecessor_id in predecessors_i)
output[rank_i] = (value_i, item_id)
```

This is a linear scatter after the RT relation is returned.  Python's
`sorted()` is called only afterward as an independent correctness oracle.

## The concrete value: one line that OptiX cannot understand

The indexed AABBs are deliberately stored in physical order `(2,0,3,1)`.
Therefore an application's nominal ID is not its GAS primitive position.

The independent PyOptiX control compiles and runs these two programs:

```cpp
// Correct application protocol
optixReportIntersection(0.0f, 0u, item.item_id);

// CP002: same U32 type, wrong application meaning
optixReportIntersection(0.0f, 0u, primitive_index);
```

The source files differ on exactly that one line.  The result on Home Linux
was:

| Program | CUDA/OptiX result | Returned relation | Sorting consequence |
| --- | --- | --- | --- |
| nominal `item_id` | CUDA success; no OptiX fatal/error | exact ten predecessor rows | stable order correct |
| physical `primitive_index` | CUDA success; no OptiX fatal/error | exact ten wrong rows | application self-identity check fails |

The wrong relation was:

```text
((0,1),(0,2),(0,3),
 (1,2),(1,3),
 (2,0),(2,1),(2,2),(2,3),
 (3,2))
```

This is the value proposition in executable form: both values are legal U32s,
and both programs are legal OptiX programs, but only one implements the
application's cross-callback identity protocol.  CUDA and OptiX executed the
wrong program without an exception.  RTDL's corresponding compiler projection
mutation is rejected by the whole-protocol gate with exactly:

```text
CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH
```

The sorting test binds this rejection to the same verified bounded-relation
callback declaration.  The pre-existing integrated lifecycle test additionally
checks that this CP002 mismatch occurs before native loading.

## Tests and hardware evidence

Local tests: **40/40 pass**.

- 19,530 exhaustive arrays: lengths 1–6, every key in `{-2,-1,0,1,2}`;
- 256 frozen random arrays: lengths 1–64, signed keys and duplicates;
- all 24×24 = 576 indexed/source physical-order pairs for the main input;
- ascending, descending, equal-key, singleton, signed, invalid and float32
  boundary cases;
- exact CP002 contract-gate rejection;
- a capacity-10 coherently wrong but complete application ordering, proving
  that RTDL admission does not prove the sorting theorem.

Home GPU functional matrix: **21/21 exact** against an independently rebuilt
pairwise relation and stable-sort oracle.

- GPU: NVIDIA GeForce GTX 1070, compute capability 6.1;
- driver: 580.173.02;
- physical receipt: `optix_traversal_observed` for every case;
- maximum valid binary32 quarter-grid case executed successfully;
- capacity 10 returned the complete relation;
- capacity 9 failed with exact `capacity_overflow@rows`, reported
  `observed_unique_count=10, materialized=9, capacity=9`, and exposed no
  application result;
- registered performance timings: zero.

The GTX 1070 has no RT cores.  This is functional OptiX traversal evidence,
not evidence of RT-core hardware use or sorting performance.

## Independent verification

`scripts/goal5830_verify_stable_sort_evidence.py` imports neither RTDL nor
PyOptiX.  From preserved raw JSON/source/PTX/native bytes it:

1. rebuilds all 21 RTDL relations and stable orders;
2. rehashes the executed example, runner, current runtime archive and native;
3. checks the PyOptiX programs differ in exactly one source line;
4. verifies the exact valid and CP002-wrong relations;
5. rehashes both PTX files and checks every recorded identity;
6. checks the complete OptiX context-message list and every pipeline-log
   string returned by the PyOptiX API, not only a filtered summary.  The API's
   returned module-log strings can themselves be truncated and are not called
   complete compiler transcripts.

Controlling verifier result:

```text
history/internal_docs/goal5830_v4_public_stable_sort_gpu_evidence_20260830/
    INDEPENDENT_VERIFICATION_V4.json
SHA-256 272fbe9b650939aacc5b6e4bf12c886e53e802216e6cca5bd39627aa1944f8b4
status PASS
```

## Exact claim boundary

This result establishes:

- the existing V4 bounded-relation family can execute this stable-sort
  mapping through the public lifecycle;
- the mapping is correct for the tested domain and 21 hardware cases;
- CP002 nominal-ID/physical-index confusion has a concrete sorting
  consequence;
- PyOptiX/OptiX alone did not reject that one-line semantic substitution;
- RTDL's whole-protocol contract gate rejects the corresponding mismatch.

It does **not** establish:

- that RTDL invented RT-based sorting;
- a new protocol or geometry family;
- arbitrary-key or production sorting;
- that RTDL verifies the application-level sorting reduction;
- performance, ease of use, unseen-app generalization or RT-core speedup.

The materialized relation is `O(n²)` in the worst case and the generic family
uses two OptiX passes plus host canonicalization.  CUB/Thrust remains the right
baseline for ordinary production sorting.  This demo exists to make RTDL's
protocol-integrity contribution understandable, not to claim a better sorting
algorithm.
