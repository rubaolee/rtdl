# Goal1741 v1.8 Source-Tree Install Boundary

## Verdict

`source_tree_boundary_validated_packaging_pending`

RTDL current `main` is usable from the source tree with `PYTHONPATH=src:.`, but it does not yet define a package-installable Python distribution. For v1.8, this must be explicit: either ship as a source-tree release with documented invocation commands, or add packaging metadata and a separate install validation gate before release.

## Packaging Metadata Audit

The repository currently has no Python packaging metadata:

- no `pyproject.toml`
- no `setup.py`
- no `setup.cfg`

This audit does not add those files. Adding packaging metadata would change the release boundary and should be done as a separate, reviewed packaging goal.

## Source-Tree Smoke Validation

The current documented source-tree invocation path was validated locally with:

```text
$env:PYTHONPATH='src;.'; py -3 examples\rtdl_hello_world.py
```

Observed output:

```text
hello, world
```

The backend-selecting source-tree path was validated locally with:

```text
$env:PYTHONPATH='src;.'; py -3 examples\rtdl_hello_world_backends.py --backend cpu_python_reference
```

Observed output included:

```json
{
  "backend": "cpu_python_reference",
  "triangle_hit_count": 2,
  "visible_hit_rect_id": 2,
  "visible_hit_label": "hello, world"
}
```

Both commands emitted the existing local Python launcher warning:

```text
Could not find platform independent libraries <prefix>
```

The warning did not prevent execution.

## v1.8 Release Implication

If v1.8 remains source-tree-only, release text must say so plainly and show the `PYTHONPATH=src:.` setup for bash/zsh and `PYTHONPATH=src;.` for Windows shells.

If v1.8 is expected to be package-installable, the release is blocked until a packaging goal adds and validates:

- package metadata
- install command
- import smoke after install
- examples smoke after install
- wheel or sdist expectations
- platform caveats for optional native backend libraries

## Boundary

This is a source-tree install boundary audit. It is not a packaging implementation, not a release packet, and not a tag authorization.
