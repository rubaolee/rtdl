# Primitive Discovery Workflow

Status: current v3.0 source-tree discovery workflow.

Use this page when you know the behavior you want, but you are not sure which
RTDL primitive, composition recipe, or partner continuation contract to inspect
first.

This workflow is metadata-only. It does not run a backend, dispatch a partner,
select a partner for you, authorize performance claims, or authorize release
readiness.

## Run The Example

From the repository root:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_primitive_discovery_workflow.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/current/getting_started/rtdl_primitive_discovery_workflow.py
```

The output is JSON with three layers:

| Output field | Meaning |
| --- | --- |
| `primitive_match` | The best primitive node for the requested intent facets. |
| `recipe_match` | The best advisory composition recipe over primitive nodes. |
| `advisory_plan` | An explain-only plan showing primitive steps, step statuses, and optional partner-support cells. |

## Step 1: Search Primitive Intent

```python
import rtdsl as rt

primitive_matches = rt.find_primitive(
    intent="nearest",
    shape="fixed_radius",
    dim="3d",
    output="grouped",
)
```

`find_primitive(...)` searches the primitive hierarchy by controlled facets
such as `intent:*`, `shape:*`, `dim:*`, `output:*`, `exactness:*`, and
`keying:*`.

Use this when you want to answer: "What primitive behavior is closest to what I
need?"

## Step 2: Search Composition Recipes

```python
recipe_matches = rt.find_recipe(
    intent="nearest",
    shape="fixed_radius",
    dim="3d",
    output="grouped",
)
```

`find_recipe(...)` searches advisory recipes built from existing primitive
nodes. Recipes explain common compositions, but they are not execution paths.

Use this when you want to answer: "Which primitive pieces commonly go
together?"

## Step 3: Ask For An Advisory Plan

```python
plans = rt.plan_continuation(
    intent="nearest",
    shape="fixed_radius",
    dim="3d",
    output="grouped",
    partner="numba",
)
```

`plan_continuation(...)` returns an explain-only plan. It can recommend a
primitive-first path or list explicit partner options, but it never sets
`selected_partner`.

Key fields:

| Plan field | Meaning |
| --- | --- |
| `recommendation` | Planning guidance such as `primitive_first` or `primitive_first_with_explicit_partner_options`. |
| `primitive_steps` | The primitive nodes used by the matched recipe. |
| `non_stable_step_ids` | Candidate/internal steps that remain non-stable even though the recipe is discoverable. |
| `partner_options` | Support-matrix cells for partner operations declared by the primitive steps. |
| `selected_partner` | Always `None`; the user chooses any partner explicitly in their own code. |
| `executes` | Always `False`; this is not a dispatcher. |
| `automatic_partner_selection_allowed` | Always `False`. |

## How To Read Partner Options

A partner option is evidence metadata, not a command.

For example, if you ask for `partner="numba"` and the current support matrix
does not support the requested operation on Numba, the plan includes an
`unsupported_fail_closed` cell. That is intentional. It tells you why the
requested partner is not currently a supported option for that operation.

RTDL's rule remains:

```text
Use a fused RTDL primitive when it exactly expresses the work.
Use a partner only when your app explicitly chooses a continuation outside the primitive.
Never rely on hidden partner dispatch.
```

## Boundaries

This workflow does not authorize:

- release readiness;
- package-install promises;
- public speedup wording;
- broad RT-core speedup wording;
- general zero-copy or device-residency wording;
- automatic partner selection;
- paper-system reproduction claims;
- app-specific native engine logic.

For the full generated primitive index, read
[RTDL Primitive Catalog And Promotion Rules](../rtdl_primitive_catalog.md).
