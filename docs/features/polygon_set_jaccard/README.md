# Polygon-Set Jaccard

## Purpose

`polygon_set_jaccard` computes one aggregate Jaccard row for a left polygon set
and a right polygon set.

Use it for narrow pathology-style polygon-set similarity where polygons satisfy
the orthogonal integer-grid unit-cell contract.

## Docs

- canonical example:
  - [rtdl_polygon_set_jaccard.py](/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_set_jaccard.py)
- generated handoff bundle:
  - [generated_polygon_set_jaccard_bundle](/Users/rl2025/rtdl_python_only/examples/rtdl_generated_polygon_set_jaccard_bundle/README.md)
- public-data audit:
  - [goal141_public_jaccard_linux_audit_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal141_public_jaccard_linux_audit_2026-04-06.md)

Kernel shape:

```python
left = rt.input("left", rt.Polygons, role="probe")
right = rt.input("right", rt.Polygons, role="build")
candidates = rt.traverse(left, right, accel="bvh")
rows = rt.refine(candidates, predicate=rt.polygon_set_jaccard(exact=False))
return rt.emit(
    rows,
    fields=["intersection_area", "left_area", "right_area", "union_area", "jaccard_similarity"],
)
```

## Code

- predicate:
  - `rt.polygon_set_jaccard(exact=False)`
- canonical reference kernel:
  - [polygon_set_jaccard_reference](/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_set_jaccard.py)

## Example

Run:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py
```

Generate a runnable handoff bundle:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle
```

## Best Practices

- keep the contract explicit: orthogonal integer-grid unit-cell polygons only
- describe the current public-data story honestly as public-data-derived after conversion
- use PostGIS-backed Linux validation when you need external correctness evidence
- use the primitive `polygon_pair_overlap_area_rows` when you need pairwise overlap detail, not only the final aggregate

## Try

- pathology mask similarity under unit-cell conversion
- aggregate left/right set similarity reports
- narrow generated handoff bundles for authored examples

## Try Not

- generic token-set Jaccard
- continuous arbitrary polygon Jaccard
- claiming mature multi-backend GPU closure for this line today

## Limitations

- narrow pathology/unit-cell contract only
- not generic continuous polygon-set Jaccard
- current strongest implementation/validation story is Python and native CPU plus Linux/PostGIS checking
