# Goal1943 - v2 Source-Tree-Only Release Decision Packet

Status: source-tree-only-policy-ready-for-external-consensus

Date: 2026-05-13

## Scope

Goal1943 turns the earlier Goal1898/1902 package-install discussion into the
current post-pod v2.0 release decision packet. It does not authorize the v2.0
release by itself. It gives external reviewers one concrete policy question:

Should v2.0 ship as a source-tree-only release, with package-install support
explicitly out of scope?

## Recommendation

Accept source-tree-only v2.0 for this release.

Allowed user-facing wording:

```text
RTDL v2.0 is used from the repository source tree. Set `PYTHONPATH=src:.` before
running examples, tests, or scripts. Package-install support is not part of this
release.
```

Blocked wording:

- `pip install rtdl`
- `pip install -e .`
- `RTDL is available as a Python package`
- `Install RTDL from PyPI`
- `Package-install support is validated`

## Why This Is The Conservative v2.0 Choice

- v2.0's main contribution is the Python+partner RTDL contract, not packaging.
- The repository still has no `pyproject.toml`, `setup.py`, or `setup.cfg`.
- Native backend discovery remains local-build and environment dependent.
- Partner dependencies are large and backend-specific, especially CUDA PyTorch
  and CuPy.
- The validated learner/developer workflow already uses `PYTHONPATH=src:.`.
- Adding packaging now would create a new release surface without the same level
  of pod, platform, and external review evidence as the v2 partner work.

## Evidence Already Available

- Goal1898 audits the current absence of packaging metadata and blocks package
  install claims.
- Goal1902 proposes the source-tree-only exception and requires 3-AI consensus.
- Goal1906 public wording scan passes while package-install claims remain
  blocked.
- Goal1907 Gemini accepted the source-tree and boundary policy with release
  still blocked.
- Goal1908 local preflight passes.
- Goal1911 now reports the remaining blockers as source-tree/package consensus,
  final v2.0 consensus, and explicit release action.
- Goal1931/1942 establish the current all-app performance rollup and keep row
  claims bounded.

## Required Consensus

This packet is ready for external consensus review, but it is not consensus on
its own.

Required before release:

1. Codex: accept this source-tree-only policy as the current engineering
   recommendation.
2. Gemini: either re-affirm Goal1907 against this post-pod packet or provide a
   new review.
3. Claude or another distinct non-Codex, non-Gemini AI: review this packet and
   either accept the policy or require packaging before v2.0.
4. Final 3-AI consensus file: explicitly states whether source-tree-only v2.0
   is accepted.
5. User release action: explicit instruction to perform the v2.0 release.

## Boundary

This policy closes only the package-install question if consensus accepts it. It
does not broaden any performance claim. The final release packet must still keep:

- row-by-row performance wording;
- four control rows out of v2 partner speedup claims;
- robot collision as positive-subsecond, not seconds-scale whole-app evidence;
- true zero-copy/direct pointer wording scoped to selected OptiX partner
  contracts;
- arbitrary PyTorch/CuPy acceleration blocked outside reviewed RTDL primitive
  calls.
