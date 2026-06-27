# Goal1944 Gemini Review - v2 Source-Tree-Only Policy

**Reviewer Identity:** Gemini CLI (as of 2026-05-13)

**Verdict:** `accept-with-boundary`

## Rationale for Verdict

Based on the comprehensive review of the provided documents, I recommend accepting the proposal for v2.0 to be released as source-tree-only, with package-install support explicitly out of scope for this release. This verdict comes with a crucial boundary condition.

The rationale for this decision is as follows:

1.  **Current State of Repository:** As highlighted in `Goal1898` and `Goal1943`, the repository currently lacks essential packaging metadata such as `pyproject.toml`, `setup.py`, or `setup.cfg`. Implementing this now would involve significant work and introduce new surface areas for review that are not central to the v2.0 release's primary objectives.
2.  **Focus of v2.0:** `Goal1943` explicitly states that v2.0's main contribution is the Python+partner RTDL contract, not packaging. Diverting resources to packaging at this stage would detract from the core value proposition of this release.
3.  **Existing Workflow:** The validated learner/developer workflow, as noted in `Goal1898` and `Goal1943`, already relies on source-tree execution via `PYTHONPATH=src:.`. This demonstrates a functional and understood method of use for the current audience.
4.  **Packaging Risks:** `Goal1898` details several risks associated with premature packaging, including the complexity of native backend discovery, large and backend-specific partner dependencies (e.g., CUDA PyTorch, CuPy), and potential conflicts with existing documentation and refresh rules.
5.  **Proposal Consistency:** `Goal1902` formally proposes this source-tree-only exception, and `Goal1943` explicitly recommends its acceptance, indicating alignment within the project's internal assessment.
6.  **Readiness Aggregator Status:** `Goal1911` explicitly lists "final source-tree-only or packaging decision lacks 3-AI release consensus" as a blocker, and `package_install_claim_authorized` is `false`, reinforcing the need for this policy decision.

## Boundary Condition

This `accept-with-boundary` verdict is contingent upon the successful completion of the "Required Consensus" outlined in `Goal1943` and `Goal1902`. Specifically, a final 3-AI consensus (Codex, Gemini, and a distinct third AI) must explicitly accept this source-tree-only policy. Until this consensus is achieved, the status of package-install support remains blocked.

This decision only addresses the package-install question and does not broaden any other performance claims or release readiness, as clearly stated in `Goal1943`, `Goal1906`, and `Goal1909`. All other release gates and evidence boundaries remain as defined in the respective goal documents.
