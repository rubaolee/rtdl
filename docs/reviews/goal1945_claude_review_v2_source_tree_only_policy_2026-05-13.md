# Goal1945 Claude Review - v2 Source-Tree-Only Release Policy

**Date:** 2026-05-13
**Reviewer:** Claude (claude-sonnet-4-6, Anthropic) -- independent of Codex and Gemini
**Verdict:** `accept-with-boundary`

---

## Question Under Review

Should v2.0 be allowed to ship as source-tree-only, with package-install support
explicitly out of scope? Or must packaging metadata be added and validated before
v2.0?

## Documents Reviewed

- `docs/reports/goal1943_v2_source_tree_only_release_decision_packet_2026-05-13.md`
- `docs/reports/goal1898_v2_package_install_gate_audit_2026-05-13.md`
- `docs/reports/goal1902_v2_source_tree_only_release_exception_proposal_2026-05-13.md`
- `docs/reports/goal1906_public_v2_claim_boundary_scan_2026-05-13.md`
- `docs/reports/goal1911_v2_readiness_aggregator.json`
- `docs/reports/goal1909_v2_release_packet_skeleton_2026-05-13.md`
- `docs/reviews/goal1907_gemini_review_v2_boundary_and_source_tree_2026-05-13.md` (for
  reference only -- not relied on for my verdict)

---

## Findings

### 1. The packaging absence is a factual repo state, not an assertion

Goal1898 records that the repository has no `pyproject.toml`, `setup.py`, or
`setup.cfg`. Only `requirements.txt` exists. This is directly verifiable from the
source tree and is not in dispute. There is no packaging metadata to validate;
source-tree-only is not a policy choice imposed on a packaged project; it
accurately describes the current state of the repository.

### 2. The existing validated workflow is already source-tree-only

All public examples, tests, and scripts documented in this release cycle use:

```bash
PYTHONPATH=src:. python3 ...
```

The README preserves this boundary. Shipping source-tree-only does not require
any documentation change that introduces a new claim; it formalizes what users
already do. This alignment between policy and practice is the correct direction.

### 3. The risks of adding packaging as an incidental pre-release step are real

Goal1898 enumerates concrete, non-trivial packaging problems:

- The import package is `rtdsl`, but historical modules exist under `src/rtdsl`;
  the public package surface requires deliberate design, not a quick metadata file.
- Native backends (Embree, OptiX) are built locally and loaded dynamically.
  `pyproject.toml` alone does not solve shared-library discovery after install.
- Optional partner dependencies (CUDA PyTorch, CuPy) are heavy and backend-
  specific. Encoding them in packaging metadata requires decisions about optional
  dependency groups that have not been reviewed.
- A premature `pip install -e .` claim would conflict with the documented refresh
  rule and existing public docs.

Adding packaging as a last-mile v2.0 gate item would introduce a new, untested
release surface with more unresolved questions than the source-tree path. That
is the wrong trade-off. A dedicated packaging design and validation goal is the
correct successor, not an incidental addition under release pressure.

### 4. The blocked-wording list is concrete and machine-checked

Goal1902/1943 define a clear allowed/blocked wording split. Goal1906 provides a
local scanner that enforces the blocked phrases across public documentation paths.
The boundary is unambiguous and does not rely on reviewer judgment at release time.

The following remain blocked regardless of this acceptance:

- `pip install rtdl`
- `pip install -e .`
- `RTDL is available as a Python package`
- `Install RTDL from PyPI`
- `Package-install support is validated`

### 5. Source-tree-only does not weaken any other gate

Goal1943 explicitly confirms, and I verify from the supporting documents, that
accepting the source-tree-only policy changes nothing about:

- row-by-row performance wording requirements;
- the four control rows excluded from v2 partner speedup claims;
- robot collision scoped as positive-subsecond, not seconds-scale whole-app evidence;
- true zero-copy / direct-pointer wording scoped to selected OptiX partner contracts;
- blocked arbitrary PyTorch/CuPy acceleration claims outside explicit RTDL primitive calls.

### 6. Goal1911 aggregator status is consistent with this review

The aggregator reports the three remaining blockers accurately:

1. Final source-tree-only or packaging decision lacks 3-AI release consensus.
2. Final v2.0 release consensus is missing.
3. Explicit user-requested release action is missing.

Pod evidence is collected, local preflight passes, and the claim boundary flags
are set correctly. My acceptance here addresses blocker (1) only.

---

## Conditions on Acceptance

This `accept-with-boundary` covers the package-install question only.

**Condition A -- Scanner coverage.** Goal1906 scans a specific set of public paths
(`README.md`, `docs/README.md`, `docs/partner_acceleration_boundaries.md`,
`docs/tutorials/*.md`). Before the final release packet is issued, the team should
confirm that no other public-facing files (e.g., CHANGELOG, installation guides,
Jupyter notebooks) contain unscanned package-install claims, or extend the scanner
to cover them.

**Condition B -- Final consensus file.** This review is one input to the 3-AI
consensus required by Goal1902/1943. It is not the consensus file itself. A
separate final 3-AI consensus artifact must explicitly record that Codex, Gemini,
and Claude each accepted source-tree-only v2.0 as the release boundary. That file
must exist before the release packet is declared complete.

**Condition C -- No release authorization.** Accepting this policy does not
authorize v2.0 release. The Goal1911 aggregator correctly shows `v2_0_release_authorized: false`.
Blockers (2) and (3) above remain open and must be resolved through the final
release consensus process and explicit user release action.

---

## Verdict

**`accept-with-boundary`**

The source-tree-only policy is the honest, conservative, and technically sound
choice for v2.0. No packaging metadata exists; the working installation method is
already `PYTHONPATH=src:.`; adding packaging metadata as a pre-release incidental
step would introduce a new, insufficiently reviewed release surface. The blocked-
wording list is concrete and machine-enforced. Accepting this policy closes the
package-install question without weakening any other v2.0 gate.

The conditions above (scanner coverage confirmation, separate final 3-AI consensus
file, no implied release authorization) must be satisfied before the release
packet is finalized.
