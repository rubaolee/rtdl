# Primitive Discovery

Status: current v2.10 source-tree tutorial.

Goal: find a reusable RTDL primitive before writing a new app path.

## Why Discovery Comes Early

RTDL is a language/runtime with generic primitives, not a fixed app library.
Before adding code, ask:

```text
What typed result do I need?
Which existing primitive already returns that result?
What continuation remains in Python or a partner?
```

## Run The Discovery Example

Linux/macOS:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_primitive_discovery_workflow.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\current\getting_started\rtdl_primitive_discovery_workflow.py
```

The example prints a small discovery flow instead of running a heavy benchmark.

## Read The Catalog

Use the current generated catalog as the reference:

- [Primitive Catalog](../../docs/rtdl_primitive_catalog.md)
- [Primitive Discovery Workflow](../../docs/learn/primitive_discovery_workflow.md)

The catalog is organized by primitive contracts and discovery metadata. App
names may appear as references, but the primitive itself should stay generic.

## A Simple Decision Rule

| If you need | Look for |
| --- | --- |
| one flag per query | an any-hit or predicate summary primitive |
| nearest distance or best witness | nearest, argmin, or top-k style primitive |
| many candidate rows | row stream or bounded witness primitive |
| grouped counts or sums | grouped reduction primitive |
| custom continuation over columns | partner-compatible typed columns |

## Next

Continue with [Python App Structure](04_python_app_structure.md).
