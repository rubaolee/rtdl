# Goal3790 AMD HIPRT Runner Prefix Discovery

Status: implemented and non-AMD pod-control validated.

## Purpose

Goal3790 hardens the Goal3785 AMD HIPRT functional pod runner for real cloud
pods. Earlier validation passed the HIPRT SDK prefix explicitly because the pod
SDK directory was version-suffixed:

`/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

The runner default was too brittle for a future AMD pod. A path mismatch should
not waste hardware time or force manual debugging.

## Change

`scripts/goal3785_amd_hiprt_functional_pod_runner.py` now:

- auto-discovers common HIPRT SDK locations, including version-suffixed
  `hiprtSdk-*` directories;
- ignores archive files that happen to match a wildcard candidate;
- honors an explicit `--hiprt-prefix` or `HIPRT_PREFIX` environment override;
- records `hiprt_prefix_resolution` in both accepted AMD artifacts and
  non-AMD control artifacts;
- prints the chosen prefix, source, and header-validity status before probing
  hardware.

The runner remains fail-closed. On non-AMD hardware it still writes only a
rejected control artifact. On AMD hardware it can produce an accepted artifact
only if the focused test suite passes and the Goal3784 validator accepts it.

## Boundary

Goal3790 does not authorize AMD performance claims, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
claims, release claims, zero-copy claims, or app-specific native-engine logic.

Actual AMD evidence still requires the Goal3785 runner on AMD hardware.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3790_amd_hiprt_runner_prefix_discovery_test tests.goal3785_amd_hiprt_functional_pod_runner_test
```

Local result:

```text
Ran 15 tests in 0.043s
OK
```

Non-AMD pod-control result:

```text
Pod: root@69.30.85.203 -p 22057
Commit: d838a797
GPU route: NVIDIA RTX A5000
Command: python3 scripts/goal3785_amd_hiprt_functional_pod_runner.py --allow-non-amd-control --non-amd-output /tmp/goal3790_non_amd_control.json
HIPRT_PREFIX: /root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
Prefix source: auto_discovered
Valid HIPRT header: True
Control status: reject_non_amd_hardware
AMD validator status: reject
```

This pod-control validation proves autodiscovery and fail-closed behavior on the
available NVIDIA/Orochi route. It is not AMD hardware evidence.
