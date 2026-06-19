# RTDL V4.0 Package Runtime Tie-Breaker

Date: 2026-06-19
Status: accepted tie-breaker decision, not release approval.

## Question

After the M8 packet, should V4.0 experimental release-candidate readiness
require package/runtime evidence, or should V4 remain source-tree-only?

## Reviewer Split

Volta recommended requiring a clean local editable install flow before V4.0 can
be called experimental release-candidate ready. The reasoning: existing
`v4_active` and `v4_release_candidate` tests insert repository paths, so they
do not prove installed import behavior.

Hilbert recommended deferring package flow and keeping
`package_install_runtime_story` open. The reasoning: `pyproject.toml` is
`rtdl-source-tree==3.0.2`, the native library is still discovered from the
checkout/build path or environment, and current evidence is deliberately not a
V4 distribution, wheel, PyPI, or stable SDK story.

## Tie-Breaker Decision

Adopt the narrow middle path:

1. Implement clean editable-install hygiene validation now.
2. Keep `package_install_runtime_story` open.
3. Do not authorize package install, PyPI, wheel, stable SDK, generated binding,
   or V4 distribution wording.

Editable install validation is a source-tree hygiene gate, not package release
evidence.

## Acceptance Criteria

- Create a fresh temporary virtual environment.
- Run `python -m pip install -e <repo>`.
- Run from a working directory outside the repository.
- Keep `PYTHONPATH` unset.
- Verify `importlib.metadata.version("rtdl-source-tree") == "3.0.2"`.
- Verify `import rtdsl` resolves through the editable checkout.
- On the Linux GPU validation host, run a minimal V4 M1 fixed-radius route smoke
  under that installed environment.
- Record native library discovery and whether it came from checkout
  `build/librtdl_optix.so`.
- Emit a machine-readable report bound to git head/tree.

## Claims Still Blocked

- PyPI;
- wheel support;
- stable SDK;
- generated binding package;
- V4 distribution artifact;
- V4.0 current release/front door;
- public true-zero-copy;
- async/nonblocking completion;
- public speedup, RTX speedup, or RT-core speedup;
- full PyTorch, full Numba, or full DLPack support;
- multi-GPU runtime support.
