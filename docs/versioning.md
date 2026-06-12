# RTDL Versioning

Status: current v2.11 source-tree guidance.

RTDL uses source-tree version markers and Git tags to identify reviewed
research snapshots. A version tag names the state of the repository and the
claim boundary attached to that state. It is not a package-install promise,
wheel promise, PyPI promise, or automatic partner-selection promise.

## Current Version

`v2.11` is the current source-tree release marker. It covers the Python+RTDL
plus explicit partner programming surface, the Embree CPU reference lane, and
the bounded NVIDIA OptiX/RT-core evidence recorded in the v2.11 release
packet.

Use the source tree directly:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
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
whole-application speedup claims, RTDL-beats-RayJoin wording, paper
reproduction wording, package-install wording, automatic partner selection,
general zero-copy/device-residency wording, or Intel/AMD GPU performance
claims.

Read the exact current boundaries in
[Current Claim Boundaries](learn/current_claim_boundaries.md).
