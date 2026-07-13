# Goal5085 Paper-App Status Model Result

Date: 2026-07-07

## Verdict Label

```text
completed_paper_app_status_model_initial_public_table
```

## Purpose

Goal5085 starts v2.14.5 by converting the RayJoin and RT-BarnesHut app experience into a shared public status model.

This is a documentation and product-boundary goal. It does not add runtime behavior.

## Implementation

Updated:

```text
Paper-reproduction-apps/README.md
```

The paper-app table now uses common columns:

```text
Paper app
RTDL language surface exercised
Bounded reproduction status
Performance status
Boundary
```

## Resulting Model

RayJoin is described as exercising:

- public planar-map LSI/PIP primitives,
- device-columnar rows,
- ordering,
- writer-free binary-operator experiments.

RT-BarnesHut is described as exercising:

- generic `AggregateHierarchy3D`,
- opening policies,
- reducers,
- CPU reference executor,
- optional Numba parity executor.

Both rows explicitly separate bounded reproduction status from performance status and from forbidden broader claims.

## Claim Boundary

The public README does not claim:

- broad all-input RayJoin performance,
- full RT-BarnesHut paper reproduction,
- RT-BarnesHut independent tree construction,
- RT-BarnesHut whole-envelope speedup,
- native/backend aggregate-hierarchy completion.

## Verification

Public-surface leak scan across:

```text
Paper-reproduction-apps/README.md
Paper-reproduction-apps/rt-barneshut-paper/README.md
src/rtdsl/aggregate_hierarchy.py
src/rtdsl/__init__.py
```

Patterns:

```text
Goal[0-9]+
call_for_review
Antigravity
Claude
Gemini
review debt
verdict
```

Result:

```text
0 matches
```

## Next Recommended Goal

Goal5086 should audit the public RTDL API surface created by RayJoin and RT-BarnesHut:

- which APIs are ready for public docs,
- which are experimental,
- which legacy/internal names remain implementation debt.
