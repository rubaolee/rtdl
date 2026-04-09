# Overlay

## Purpose

`overlay` in RTDL is a narrow overlay-seed workload, not full polygon overlay
materialization.

Use it when you want candidate polygon/polygon overlap pairs plus flags that
indicate exact follow-up work.

## Docs

- canonical kernel pattern:
  - [rtdl_language_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_language_reference.py)
  - [rtdl_codex_authored.py](/Users/rl2025/rtdl_python_only/examples/internal/rtdl_codex_authored.py)
- language contracts:
  - [dsl_reference.md](/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md)
  - [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

Kernel shape:

```python
left = rt.input("left", rt.Polygons, role="probe")
right = rt.input("right", rt.Polygons, role="build")
candidates = rt.traverse(left, right, accel="bvh")
seeds = rt.refine(candidates, predicate=rt.overlay_compose())
return rt.emit(
    seeds,
    fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
)
```

## Code

- predicate:
  - `rt.overlay_compose()`
- canonical reference kernel:
  - [county_soil_overlay_reference](/Users/rl2025/rtdl_python_only/examples/rtdl_language_reference.py)

## Example

Start here:

- [rtdl_language_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_language_reference.py)
- [rtdl_codex_authored.py](/Users/rl2025/rtdl_python_only/examples/internal/rtdl_codex_authored.py)

## Best Practices

- describe it honestly as an overlay-seed or overlap-pair workload
- use it when downstream code will run exact follow-up logic outside this feature
- keep emitted seed ids stable for later joins
- point readers to the limitation that this is not final polygon output

## Try

- overlap-pair generation
- seed generation for later exact processing
- audit rows that need `requires_lsi` and `requires_pip` flags

## Try Not

- claiming full `ST_Intersection`-style output
- using it as if it produced final clipped polygons
- using it as the first choice for area-based overlap/Jaccard tasks

## Limitations

- not full polygon overlay materialization
- still a narrower analogue feature in the current system story
- if you need overlap area or Jaccard, use the newer narrow Jaccard line instead
