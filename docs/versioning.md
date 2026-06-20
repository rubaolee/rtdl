# RTDL Versioning

Status: current V4.0.0 source-tree guidance.

RTDL uses source-tree version markers and Git tags to identify reviewed
research snapshots. A version tag names the state of the repository and the
claim boundary attached to that state. It is not a package-install promise,
wheel promise, PyPI promise, or automatic partner-selection promise.

## Current Version

`v4.0.0` is the current source-tree release marker. It is the first V4 release:
the Python GPU RT-core operator lane for the fixed-radius CUDA device-array
route, with CuPy, Numba, and PyTorch evidence for that exact route. The V3.0.2
ten-app benchmark route matrix remains documented as the previous release line.

Use the source tree directly:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py
make build-optix
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py
```

Optional editable installs are only local developer convenience. They do not
turn RTDL into a distribution package.

## Tag Policy

- A version tag should point at a commit that contains the matching version
  marker and release packet.
- A version tag should keep compact summaries, reproduction scripts, and public
  wording boundaries in tree.
- Large raw pod logs, scratch clones, build directories, cache files, and
  per-run benchmark payloads should stay out of the source release.
- Moving a published tag requires explicit maintainer authorization and a
  written reason in the release notes.

## Claim Boundary

Version wording does not authorize broad RT-core speedup claims,
whole-application speedup claims, RTDL-beats-specialized-code wording, paper
reproduction wording, package-install wording, stable SDK wording, generated
binding wording, automatic partner selection, device-buffer C ABI query
execution, external CUDA stream ordering, general zero-copy/device-residency
wording, or Intel/AMD GPU performance claims.

Read the exact current boundaries in
[Current Claim Boundaries](learn/current_claim_boundaries.md).
