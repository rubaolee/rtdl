# Goal1898 - v2 Package-Install Gate Audit

Status: blocked-source-tree-only-until-consensus

Date: 2026-05-13

## Scope

Goal1898 audits the v2.0 package-install blocker from the stricter Goal1814
birth gate. It does not add packaging metadata and does not authorize package
installation claims.

## Current State

The repository currently has:

- `requirements.txt`
- no `pyproject.toml`
- no `setup.py`
- no `setup.cfg`

The current public and validation workflow remains source-tree execution:

```bash
PYTHONPATH=src:. python3 -m unittest ...
PYTHONPATH=src:. python3 examples/...
```

The README and docs already preserve this boundary by saying the current release
is source-tree Python+RTDL and does not promise package-install support.

## Why This Is Still A v2.0 Gate

Goal1814 allows two ways to close the package-install blocker:

1. Add packaging metadata and validate the install commands.
2. Keep v2.0 explicitly source-tree-only by reviewed consensus.

Codex should not silently choose either policy alone. If we add packaging, we
need to decide the public package surface, included native/source assets, optional
dependencies, and how Embree/OptiX dynamic libraries are discovered after
install. If we keep source-tree-only, that exception must be ratified by the
required external reviews and final v2.0 consensus.

## Packaging Risks To Resolve Before Adding Metadata

- The public import package is `rtdsl`, but the repository also contains many
  historical and report-oriented modules under `src/rtdsl`.
- Native backends are built locally and loaded dynamically; package metadata
  alone does not solve Embree/OptiX shared-library discovery.
- Optional partner dependencies are heavy and backend-specific:
  - PyTorch CUDA;
  - CuPy CUDA;
  - NumPy CPU path.
- Source-tree examples and tests rely on `PYTHONPATH=src:.` and local repo
  layout.
- A premature `pip install -e .` claim would conflict with the refresh rule and
  existing public docs.

## Current Decision

Do not add packaging metadata as an incidental change inside performance work.

The package gate remains open. The next acceptable actions are:

- create a dedicated packaging design and validation goal; or
- write a dedicated v2.0 source-tree-only release exception proposal and send it
  for required external review.

Until then, all v2.0 docs and reports must keep package-install claims blocked.
