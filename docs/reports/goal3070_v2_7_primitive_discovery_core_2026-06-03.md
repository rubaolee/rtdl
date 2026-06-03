# Goal3070: v2.7 Primitive Discovery Core

Date: 2026-06-03

Status: implemented locally, pending external review.

## Purpose

v2.6 closed the Numba-partner release lane. The first v2.7 design problem is
that RTDL's primitive hierarchy is organized correctly for governance but not
for discovery: users ask for intent, shape, output, and backend support, while
the current hierarchy is arranged by dependency layer.

This goal implements the first slice of the Claude design note
`docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`.

## What Changed

Added a metadata overlay to `PrimitiveHierarchyNode`:

- `capability_tags`
- `aliases`
- `intent_phrases`
- `reference_path`
- `backends`
- `partner_ops`
- `considered_alternatives`
- `distinct_from`

Added a controlled capability vocabulary in `src/rtdsl/primitive_hierarchy.py`:

- `intent:*`
- `shape:*`
- `dim:*`
- `output:*`
- `exactness:*`
- `keying:*`

Added `src/rtdsl/primitive_discovery.py` with:

- `primitive_index()`
- `find_primitive(...)`
- `describe_primitive(node_id)`
- `lint_new_primitive(candidate_node)`

The first indexed nodes are intentionally app-independent primitives and
continuations:

- `traversal.any_hit`
- `traversal.count_hits`
- `traversal.fixed_radius_count_threshold`
- `rows.ray_triangle_hit_stream_3d`
- `rows.fixed_radius_neighbor_rows`
- `materialization.collect_k_bounded`
- `reduction.grouped`
- `reduction.ray_triangle_primitive_grouped_i64`
- `continuation.segmented_chunked_rows`
- `continuation.ranked_summary`

## Duplicate Gate

`lint_new_primitive()` compares a candidate primitive's key facets against the
existing hierarchy. If a candidate appears to duplicate an existing primitive
and does not provide both `considered_alternatives` and `distinct_from`, the
lint fails closed.

This does not automatically reject all similar work. It forces a design author
to explain why a new primitive is different from the existing one before it can
be promoted.

## Boundary

This goal does not:

- change native engine ABI;
- add app-specific primitives;
- choose a partner automatically;
- claim performance improvement;
- claim release readiness;
- generate the Markdown catalog from the Python nodes.

Catalog generation and orchestration recipes remain future v2.7 work.

## Verification

Ran on Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test
```

Result:

```text
Ran 12 tests in 0.021s

OK
```

Also ran:

```powershell
py -3 -m py_compile src/rtdsl/primitive_hierarchy.py src/rtdsl/primitive_discovery.py src/rtdsl/__init__.py
```

Result: clean.
