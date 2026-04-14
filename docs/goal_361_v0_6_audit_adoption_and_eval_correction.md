# Goal 361: v0.6 audit adoption and evaluation correction

## Why

The detailed Gemini audit found a real flaw in the `v0.6` graph evaluation
harness: PostgreSQL timing was measured as repeated setup+query work rather than
query-only work. Claude also identified several lower-risk cleanup items and
expanded the test surface.

This goal exists to adopt those findings explicitly instead of leaving them as
loose review artifacts.

## Scope

In scope:
- adopt the Gemini detailed audit as an active engineering artifact
- fix the PostgreSQL timing methodology in `graph_eval.py`
- adopt the low-risk Claude fixes that fit the current bounded slice
- rerun the affected Linux graph evaluations
- update the affected `v0.6` reports to supersede the old timing claims

Out of scope:
- new graph workloads
- new backends
- full paper-scale benchmarking

## Closure

Close when:
- the timing split is real in code
- the corrected Linux numbers are recorded in the affected reports
- the old combined PostgreSQL timing interpretation is explicitly superseded
