# Goal1679 Pod Full-Suite Triage

Date: 2026-05-10

Status: broad-suite triage for the v1.8 Python+RTDL track.

## Command

After staging the current source tree on the RTX A5000 pod and provisioning
Embree/GEOS development dependencies, the broad unittest discovery command was
run:

```text
cd /tmp/rtdl_goal167x_validate
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

## Result

```text
Ran 3613 tests in 332.008s
FAILED (failures=65, errors=31, skipped=283)
```

This is not a v1.8 release pass.

## Triage

The focused current gate remains green:

```text
Ran 49 tests
OK (skipped=1)
```

`make build` and `make build-embree` also pass on the pod. The broad discovery
failure set is dominated by historical public-doc pinning tests, old release
surface synchronization tests, generated packet writer tests, and
OptiX-dependency-sensitive profiler tests.

One concrete stale expectation was fixed locally after this run:

- `tests/goal760_optix_robot_pose_flags_phase_profiler_test.py` now accepts the
  current `packed_arrays` error text that names both `embree` and `optix`.

## Release Meaning

For v1.8, the broad-suite result means Python+RTDL productization still needs a
deliberate release-gate cleanup pass:

- decide which historical doc-pinning tests remain active gates;
- either update or retire stale tests that conflict with the current compact
  public docs;
- keep the current app-agnostic native gate separate from old RTX/public
  speedup wording gates;
- keep OptiX runtime tests blocked until the SDK header dependency is resolved.

The focused v1.8/v2.0 architecture gate is green, but the repository-wide test
suite is not yet a release-quality green bar.
