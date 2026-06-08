# Goal3979: Short Row Scale Calibration Probe

Date: 2026-06-08

## Purpose

Goal3978 showed that two current scale-profile rows have higher relative
range because their wall-clock rows are short:

- `robot_collision_optix_scale_default_1024_no_probe_reference`
- `raydb_style_optix_count_scale_default_262k`

Goal3979 probes the simplest possible calibration idea: keep the same contract
and increase only the internal repeat count.

## Probe

The pod ran:

- Robot collision with `--repeats 30` instead of the registry value `5`.
- RayDB count with `--repeat 25` instead of the registry value `5`.

Both probes used the Goal3976 fresh checkout and the same RTX 4000 Ada
toolchain.

## Findings

### Robot Collision

The robot collision probe produced 30 repeated runs, but the hot traversal work
remained tiny:

- app lowering: 0.539s
- tail prepare build: 0.115s
- tail prepared-query build: 0.177s
- tail traversal: 0.000040s
- tail total run: 0.000062s

Increasing repeats does not create a useful 10-second RT workload for this
row. The row mostly measures process/setup/lowering envelope plus prepared
query construction, not enough hot traversal.

### RayDB Count

The RayDB probe recorded `prepared_internal_repeat: 25`, but the promoted hot
path still ran in about 1 ms:

- median-like final `elapsed_sec`: 0.000921s
- native call wall: 0.000605s
- traversal: 0.000211s
- cold prepare total: 0.406s

The scale runner's multi-second wall time for this row is therefore mostly
Python process/import/setup and artifact envelope. Increasing internal repeat
count alone does not produce a claim-grade row-duration metric.

## Conclusion

Do not update the current scale registry by merely increasing repeat counts for
these rows. That would make the packet look longer without measuring the
hot-path work we care about.

The next benchmark-quality target should be a metric contract change:

- separate process/setup envelope from hot-path medians in the current-scale
  registry;
- add a `target_hot_path_duration_sec` or `representative_hot_path_metric`
  field for rows whose application output already records phase timing;
- if claim-grade timing is required, scale data size or batch count until the
  measured hot path, not the subprocess wrapper, reaches the target duration.

## Boundary

This is a negative calibration probe and planning report. It does not authorize
release, public-speedup wording, whole-app acceleration wording, broad RT-core
wording, true-zero-copy wording, AMD performance wording, paper reproduction,
package-install wording, automatic partner/backend selection, or app-specific
native-engine logic.
