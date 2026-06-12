# Gemini Review: Goal4301-Goal4308 Fable5 Action Packet

Date: 2026-06-11
Reviewer: Gemini (autonomous CLI agent)
Verdict: `accept`

## Summary

This review evaluates the concrete actions taken in the Goal4301-Goal4308 packet following the Claude Fable5 whole-project critical review. The implementation demonstrates exceptional discipline in addressing security hygiene, architectural debt, and claim honesty without overextending the project's public boundaries.

## Findings

### 1. Security and Hygiene (Goal4303)
Goal4303 successfully addressed the F1 high-severity finding. Root-level debris and private-key-shaped files were removed from the repository. `.gitignore` was hardened with specific patterns for secrets and archives. Most importantly, a current-goal redaction guard (`tests/goal4303_current_security_redaction_guard_test.py`) was implemented to prevent future leakage of pod connection strings, raw IPs, or key names in reports and handoffs.

### 2. Numba Generic Top-K (Goal4301)
The implementation of `grouped_topk_f64` in `numba_partner_continuation.py` successfully retires the host-rank materialization debt. The primitive is generic, using a CUDA kernel for equal contiguous segments. It avoids app-specific vocabulary (RTNN/ANN) in its runtime implementation, adhering to the project's app-agnostic engine mandate.

### 3. Partner-Column Contracts (Goal4306)
The introduction of `RtdlGroupIdContract` and `RtdlPartnerClaimBoundary` provides a solid foundation for the partner-adapter refactor (F3/P2). By making the group-id layout and claim boundaries explicit and false-by-default, the project significantly reduces the risk of "copy-paste metadata" errors. The `partner_adapters.py` monolith remains, but the first structural slice is correctly implemented.

### 4. Evidence Honesty and Process (Goal4305)
The `RT-Core Evidence Matrix` (`docs/learn/rt_core_evidence_matrix.md`) is a critical addition for internal honesty. It conservatively classifies benchmark apps and explicitly states that the ten-app packet is not ten broad RT-core speedup claims. The two-tier goal protocol (P12) correctly allows for ceremony reduction on low-risk hygiene tasks while maintaining rigor for runtime and claim work.

### 5. Onboarding and RTNN Front Door (Goal4307, Goal4308)
Goal4307 improves learner ergonomics via an optional editable source-tree path without making a public package-install claim. Goal4308 honestly closes the RTNN Embree gap by adding an `ann_embree_quality` mode, explicitly labeled as a 2-D candidate-quality contract rather than a full 3-D RTNN paper reproduction.

## Answers to Review Questions

1. **Did Goal4303 materially address Fable5 F1 for the current active tree?**
   Yes. It removed root debris, hardened `.gitignore`, and implemented a redaction guard that successfully scans goal42xx/43xx evidence for secrets and connection details.

2. **Is the security scope honest?**
   Yes. The documentation and tests explicitly state that the redaction guard targets the current active surface (goal42xx/43xx) and that a broader historical archive pass is still required.

3. **Did Goal4301 correctly implement generic Numba `grouped_topk_f64`?**
   Yes. The implementation is generic, ranks on-device without host materialization, and rejects malformed layouts through a device-resident error flag.

4. **Did Goal4306 make the partner-column contracts explicit enough to close the first slice of Fable5 P2?**
   Yes. `RtdlGroupIdContract` and `RtdlPartnerClaimBoundary` provide the necessary types and metadata to begin the refactor. The report is honest about the fact that the full `partner_adapters.py` split remains open work.

5. **Does Goal4305 classify RT-core evidence conservatively enough?**
   Yes. It correctly uses "Mixed", "Partner-led", and "Coverage" labels where appropriate and contains the mandatory sentence: "the ten-app packet is not ten broad RT-core speedup claims."

6. **Does Goal4307 improve source-tree onboarding without creating a public package-install claim?**
   Yes. The editable install path is documented as a local convenience, and the README explicitly disclaims any distribution-package or PyPI promise.

7. **Does Goal4308 remove the RTNN Embree packet special case honestly?**
   Yes. It adds the `ann_embree_quality` mode and explicitly documents that it is not the 3-D RTNN ranked-summary path and not full RTNN paper reproduction.

8. **Which remaining Fable5 items should be next?**
   The **Kernel-DSL bridge pilot (P4)** and the **1-second timing-floor packet (P5)** are the highest-leverage remaining items. P4 resolves the strategic identity of the language, and P5 ensures the next profiling packet meets the project's own rigor standards. **Archive/report curation (P9)** and **Prose deduplication (P10)** should follow as hygiene/readability tasks.

## Claim Boundaries

This review **does not authorize**:
- release action or tags,
- public package-install or PyPI wording,
- broad RT-core speedup claims,
- whole-application acceleration claims for the ten benchmark apps,
- paper-reproduction wording (RTNN, RayJoin, etc.),
- true zero-copy or device-residency claims,
- automatic partner selection.
