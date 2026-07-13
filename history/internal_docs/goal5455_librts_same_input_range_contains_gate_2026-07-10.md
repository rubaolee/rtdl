# Goal5455 - LibRTS Same-Input Range-Contains Gate

Date: 2026-07-10

## Objective

Extend the bounded LibRTS line from point containment to envelope containment,
while explicitly distinguishing the direction:

```text
indexed_box_contains_query_box
```

## Semantic Audit

The pinned author source calls `envelope.Contains(query)` in
`shaders_contains_envelope_query_2d.cu`. `Envelope::Contains` uses inclusive
minimum/maximum comparisons in every dimension. The RTDL contract records the
same semantics.

The fixture is deliberately asymmetric:

```text
correct indexed-box-contains-query count = 5
reversed query-contains-indexed-box count = 2
```

Therefore a direction reversal cannot pass by count coincidence.

## Environment And Input Identity

The gate reuses the Goal5454 pinned author build and RTDL OptiX build on
`lx1 / 192.168.1.20` (GTX 1070). Embree is not built or executed.

```text
author commit = 52509e8022abeab722f5a9a89d1917e8b481defe
tiny_boxes.wkt sha256 = 12629026e7323d795d00407a3ac7b11206eca18b442ac8357b2870e57922e3f2
tiny_range_queries.wkt sha256 = 72a363f6394d69cc1d508ac12854d43300f526d1eb662365621548c3633f86df
expected JSON sha256 = 1377ac9edcd091a5e0ffe0f5c999ca1926985b0db4a86a0cd80509e880081f58
same files passed to author and RTDL = true
```

## Result

```text
author RTSpatial/OptiX count = 5
RTDL OptiX count = 5
direction-discriminating fixture = true
RTDL rt_core_accelerated = true
RTDL native_engine_customization = false
matched = true
```

RTDL's exact fixture oracle rows are:

```text
(0,0), (0,1), (1,0), (3,2), (4,3)
```

The public RTDL API is `query_aabb_index_2d(operation="range_contains")`.
It exposes native count, not native pair rows. The author example also exposes
count only. The pair rows above are an app-owned exact fixture oracle and are
not presented as either implementation's native row output.

Evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5455_same_input_range_contains.json
```

## Validation

```text
Goal5455 local tests = 3 OK
Goal5453-5455 focused local/portfolio slice = 24 OK
Goal5455 Linux tests = 3 OK
author/RTDL OptiX live gate = matched
```

## Timing Boundary

The author artifact records one diagnostic (`load 2.436ms`, `query 0.083ms`).
There is no denominator-aligned RTDL timing. No performance claim or ratio is
authorized, and local GTX 1070 evidence is functional only.

## Claim Boundary

Authorized:

- one bounded same-input range-contains count agreement;
- a direction-discriminating exact fixture oracle;
- public generic RTDL AABB count API execution on OptiX.

Not authorized:

- author/RTDL pair-row equality;
- range-intersects agreement;
- mutable index parity;
- Ray Multicast/PIP equivalence;
- paper dataset, figure, full reproduction, or performance claims;
- Embree evidence or a LibRTS-specific RTDL primitive.

## Next Goal

Goal5456 should run a discriminating same-input `range_intersects` fixture
through author RTSpatial/OptiX and RTDL OptiX. The existing generic
`aabb_intersection_pair_rows_2d` API may provide RTDL rows, but the count-only
author example still limits author agreement to count unless separately
instrumented.

## Exit Label

```text
goal5455_librts_same_input_range_contains_count_matched__review_pending
```
