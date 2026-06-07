# Goal3785 AMD HIPRT Functional Pod Runner

Status: implemented locally; non-AMD negative-control pod run pending.

## Purpose

Goal3785 adds the executable runner for the Goal3784 AMD HIPRT functional
validation contract:

`scripts/goal3785_amd_hiprt_functional_pod_runner.py`

The runner is intentionally fail-closed. It can produce the accepted Goal3784
artifact only when the host probe identifies actual AMD hardware. On NVIDIA or
unknown hardware it writes a separate negative-control artifact and refuses to
count that output as AMD evidence.

## Usage

On an actual AMD pod:

```text
PYTHONPATH=src:. python3 scripts/goal3785_amd_hiprt_functional_pod_runner.py --hiprt-prefix /path/to/hiprtSdk
```

The accepted AMD artifact path is:

`docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`

On a non-AMD pod, for runner validation only:

```text
PYTHONPATH=src:. python3 scripts/goal3785_amd_hiprt_functional_pod_runner.py --allow-non-amd-control
```

That writes:

`docs/reports/goal3785_non_amd_hiprt_functional_runner_control.json`

The non-AMD control artifact is useful for proving the runner cannot mint AMD
evidence on NVIDIA. It is not AMD hardware evidence.

## Boundary

Goal3785 does not authorize AMD performance claims, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
claims, release claims, zero-copy claims, or app-specific native-engine logic.

The runner only automates the future AMD functional validation step. It does not
replace the need for actual AMD hardware.

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3785_amd_hiprt_functional_pod_runner_test tests.goal3784_amd_hiprt_functional_validation_runbook_test
```
