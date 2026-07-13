# Goal4920 Planar-Map Workspace User Example

Status: completed, pending external review.

## Purpose

Goal4920 added a small runnable example showing how an app author combines the
public planar-map workspace, LSI, point-location/PIP, and a tiny app-owned
continuation. The example deliberately avoids "one call does everything" style.

## Added Example

`examples/current/features/spatial/rtdl_planar_map_workspace_lsi_pip.py`

The example:

1. writes two tiny CDB-like planar-map fixtures to a temporary directory;
2. prepares `prepare_planar_map_workspace_2d_optix`;
3. runs `run_lsi_pair_id_rows`;
4. runs left-in-right and right-in-left point-location;
5. summarizes positive face ids with a small Python continuation, using Numba
   if available;
6. prints structured JSON.

## User Lesson

The example teaches this programming shape:

```text
public RTDL workspace owns prepared primitive handles
-> public primitive calls emit rows
-> app-owned Python or partner continuation consumes rows
```

It does not import `rtdsl.rayjoin_overlay`, does not implement polygon overlay,
and does not hide application output assembly inside RTDL core.

## Local Validation

Commands run from the repository root:

```powershell
py -m py_compile examples/current/features/spatial/rtdl_planar_map_workspace_lsi_pip.py
$env:PYTHONPATH='src'; py examples/current/features/spatial/rtdl_planar_map_workspace_lsi_pip.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4913_planar_map_workspace_api_test
```

Results:

- compile: passed;
- local Windows run: exited successfully with structured `status: skipped`
  because the local machine has no CUDA driver for the OptiX backend;
- workspace API unit tests: 4 tests passed.

The skip behavior is intentional for non-OptiX local machines. On an OptiX
machine the same example exercises the real workspace path.

## Exit Label

`completed_workspace_example_runnable_public_shape_no_rayjoin_helper`
