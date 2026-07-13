# Goal4918 Clean Integration And Public/Private Boundary Audit

Status: completed, pending external review.

## Purpose

Goal4918 closed the public/private integration gap left by the planar-map
workspace API. The API was already exported and tested as public, but the user
surface did not yet explain it. The goal was to make the public surface
consistent without leaking internal review/process material.

## Actions

1. Confirmed `PlanarMapWorkspace2DOptix` and
   `prepare_planar_map_workspace_2d_optix` are public exports in
   `src/rtdsl/__init__.py`.
2. Confirmed existing tests assert:
   - the workspace is exported through `rtdsl`;
   - it prepares public LSI and point-location sessions;
   - it does not import the bundled RayJoin overlay helper;
   - it does not expose raw OptiX callbacks.
3. Added a public feature page:
   - `docs/features/planar_map_workspace/README.md`
4. Linked that page from:
   - `docs/features/README.md`
   - `docs/features/lsi/README.md`
   - `docs/features/pip/README.md`
   - `examples/current/features/README.md`
5. Removed the public-facing word "internal" from the primitive catalog status
   line:
   - `docs/rtdl_primitive_catalog.md`

## Public Boundary

The workspace is public and generic at the API boundary. It is allowed to say:

```text
RTDL exposes a reusable OptiX planar-map workspace that prepares public LSI and
point-location sessions once, then leaves app-specific continuation and output
assembly outside RTDL core.
```

It is not allowed to say:

```text
The workspace is a RayJoin overlay primitive.
The workspace exposes raw OptiX callback programming.
The workspace authorizes broad RayJoin or RTDL speedup claims.
```

## Verification

Commands run from the repository root:

```powershell
rg -n "Goal[0-9]+|Claude|Gemini|Antigravity|Codex|V3|V4|Phoenix|call_for_review|verdict|review debt|redo_required|generated internal" README.md docs examples/current -g "*.md" -g "*.py"
$env:PYTHONPATH='src'; py -m unittest tests.goal4913_planar_map_workspace_api_test
```

Results:

- public leak scan: no matches;
- workspace API tests: 4 tests passed.

## Exit Label

`completed_public_workspace_boundary_integrated_no_process_leak`
