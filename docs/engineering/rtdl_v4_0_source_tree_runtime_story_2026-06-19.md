# RTDL V4.0 Source-Tree Runtime Story

Status: experimental V4 M1 source-tree runtime evidence, not a package release.

Date: 2026-06-19

## Boundary

V4.0 M1 currently has a source-tree runtime story only.

It does not have a V4 package install story, PyPI artifact, wheel, stable SDK,
or generated binding package. The local editable metadata in `pyproject.toml`
is for checkout convenience and currently names the source-tree package
`rtdl-source-tree` at version `3.0.2`; it is not a V4 distribution artifact.

## Supported Source-Tree Flow

From a checkout:

```bash
PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --include-v4-active --json
make build-optix
PYTHONPATH=src:. python3 scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_active
PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_numba_partner_surface_probe.py
PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_dlpack_capsule_probe.py
PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe.py
```

For the current V4 M1 route, Linux GPU runtime evidence requires:

- Python able to import `rtdsl` from the checkout;
- NumPy;
- CuPy, Numba, and PyTorch for the evidence-backed Python GPU partner paths;
- CUDA driver/runtime tooling sufficient for CuPy, Numba, and PyTorch;
- OptiX SDK headers and CUDA compiler/runtime libraries for `make build-optix`;
- `build/librtdl_optix.so` reachable from the checkout.

## Validated Preflight

Windows local source-tree doctor:

- command: `py -3 scripts/rtdl_source_tree_doctor.py --include-v4-active --json`;
- result: `ok=true`;
- required failures: none;
- V4 active experimental ABI surface: pass;
- optional editable source-tree metadata: pass;
- optional CuPy, Numba, and OptiX library: warn on this Windows host.

Linux `192.168.1.20` source-tree doctor:

- command:
  `PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --include-v4-active --json`;
- result: `ok=true`;
- required failures: none;
- V4 active experimental ABI surface: pass;
- optional editable source-tree metadata: pass;
- CuPy: pass;
- Numba: pass;
- PyTorch: pass after user-site `torch==2.12.1+cu126` install on the source-tree validation host;
- OptiX library: pass after `make build-optix`;
- optional Embree library: warn, not required for V4 M1.

Latest Linux V4 gate on `192.168.1.20` for head
`66e6529859a1bac63ce2a72527dc5942e301143d`:

- `make build-optix`: pass;
- source-tree runtime preflight with `--require-v4-gpu-runtime`: pass;
- `v4_active`: 71 tests, pass;
- `v4_release_candidate`: 71 tests, pass as a non-authorizing review gate;
- Numba M1 `DeviceNDArray` fixed-radius route probe: pass;
- DLPack capsule fixed-radius route probe: pass;
- PyTorch CUDA tensor fixed-radius route compatibility probe: pass;
- front-door claim-boundary scan: pass;
- `git diff --check`: pass;
- worktree clean.

Package/runtime hygiene validation on `192.168.1.20` for source-tree head
`1ad0a1437b38a3a043948ee96afc216dffe844a1`:

- `make build-optix`: pass;
- source-tree runtime preflight with `--require-v4-gpu-runtime`: pass;
- `v4_active`: 73 tests, pass;
- `v4_release_candidate`: 73 tests, pass as a non-authorizing review
  gate;
- editable-install hygiene probe with `--system-site-packages --run-v4-smoke`:
  pass;
- the host lacks ensurepip, so the probe fell back to
  `venv --without-pip` plus `pip --python` while still using a fresh temporary
  venv;
- the editable probe ran from a working directory outside the repository with
  `PYTHONPATH` unset;
- `rtdsl` resolved through the editable checkout;
- native library discovery found `build/librtdl_optix.so` under the checkout;
- V4 M1 CuPy smoke produced the expected fixed-radius output columns;
- `git diff --check`: pass;
- worktree clean.

Tracked machine-readable report:

`docs/reports/v4_0_source_tree_runtime_preflight_2026-06-19.json`

That report is bound to Linux head
`1ad0a1437b38a3a043948ee96afc216dffe844a1` and records:

- source-tree import from `src/rtdsl`;
- `pyproject.toml` identity as `rtdl-source-tree` version `3.0.2`;
- V4 active doctor checks with CuPy, Numba, PyTorch, and OptiX library all
  passing;
- `v4_active` and the non-authorizing `v4_release_candidate` review gate
  exposed;
- package install, PyPI, wheel, stable SDK, generated binding, and V4 front-door
  claims all unauthorized.

## Package Blocker

`package_install_runtime_story` remains open.

The package/runtime tie-breaker is:

`docs/reviews/codex_v4_package_runtime_tiebreaker_2026-06-19.md`

It requires editable-install hygiene evidence as a source-tree gate, while
keeping package/PyPI/wheel/stable SDK claims blocked.

Editable-install hygiene evidence:

`docs/reports/v4_0_editable_install_runtime_probe_2026-06-19.json`

That report must be read narrowly. It validates a temporary local editable
checkout install with `PYTHONPATH` unset and the working directory outside the
repository, then runs one Linux V4 M1 CuPy smoke against the checkout native
library. It is not a V4 distribution artifact.

Closing it requires a V4 package flow, such as a tested wheel or equivalent
reviewed package/install path, in a clean environment. A future closure packet
should include:

- exact artifact name and version;
- install command;
- dependency/runtime expectations;
- clean-environment import smoke;
- V4 M1 route smoke after install;
- native library discovery behavior;
- compatibility and uninstall/reinstall behavior;
- claim-scan evidence proving docs say only what the package flow proves.

Until then, allowed wording is:

"V4.0 M1 has a validated source-tree runtime path for engineering review."

Blocked wording remains:

- package install;
- PyPI;
- wheel support;
- stable SDK;
- generated binding package;
- V4.0 as the current user front door.
