# RTDL Language Docs

This directory is the language-facing documentation for the current RTDL surface.

RTDL is currently a Python-hosted language with a constrained kernel subset. The
host language is Python, but only a small RTDL authoring model is considered part
of the language:

- `@rt.kernel(...)`
- `rt.input(...)`
- `rt.traverse(...)`
- `rt.refine(...)`
- `rt.emit(...)`
- the currently supported geometry types, layouts, predicates, and emit schemas

The current language coverage is intentionally limited to six workload families:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

Read these files in order:

1. `dsl_reference.md`
2. `programming_guide.md`
3. `workload_cookbook.md`
4. `llm_authoring_guide.md`

These documents are written as the authoritative language reference for the
current compiler surface, not as future-looking design notes.

The current RTDL toolchain now has two usable modes:

- compile/lower/codegen for backend planning
- `rt.run_cpu(...)` for local execution of the currently supported workloads
- `rt.run_embree(...)` for native local execution on macOS with Embree installed

The language docs in this directory are intended to describe the current public
surface, including the two Goal 10 workload extensions.
