# RTDL Versioning

Status: current v3.0.2 source-tree guidance.

RTDL uses source-tree version markers and Git tags to identify reviewed
research snapshots. A version tag names the state of the repository and the
claim boundary attached to that state. It is not a package-install promise,
wheel promise, PyPI promise, or automatic partner-selection promise.

## Current Version

`v3.0.2` is the current source-tree release marker. It is a patch release for
the V3.0 line: the Python+RTDL plus explicit partner programming surface, the
closed ten-app benchmark route matrix, and the V3 app-author
primitive-first/explicit-partner guidance remain the product surface, while the
patch release records the post-release boundary cleanup.

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
whole-application speedup claims, RTDL-beats-specialized-code wording, paper
reproduction wording, package-install wording, stable SDK wording, generated
binding wording, automatic partner selection, device-buffer C ABI query
execution, external CUDA stream ordering, general zero-copy/device-residency
wording, or Intel/AMD GPU performance claims.

Read the exact current boundaries in
[Current Claim Boundaries](learn/current_claim_boundaries.md).
