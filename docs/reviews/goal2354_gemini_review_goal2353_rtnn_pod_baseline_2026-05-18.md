# Gemini Review for Goal2353 RTNN Pod Baseline - 2026-05-18

**Reviewer:** Gemini (Independent AI Reviewer)
**Date:** 2026-05-18

---

## Disclaimer

As an independent Gemini reviewer, this assessment is conducted without influence from Codex. This review does not represent a Codex+Codex consensus.

---

## Review Questions and Answers

### 1. Does Goal2353 correctly preserve the claim boundary, especially that the successful RTNN rows do not imply RTDL speedup or RTDL/RTNN parity yet?

_Answer:_ Yes. The "Claim Boundary" section in `docs/reports/goal2353_v2_2_rtnn_pod_baseline_2026-05-18.md` explicitly states what the goal does *not* authorize, including RTDL speedup claims, broad RT-core speedup claims, or claims of RTDL reproducing RTNN. It clearly limits authorization to the conclusion that both external RTNN and RTDL OptiX runtime are runnable on the same RTX A5000 pod. This boundary is consistently reinforced in the `claim_boundary` fields within the JSON artifacts and verified by the tests in `tests/goal2353_v2_2_rtnn_pod_baseline_test.py`.

### 2. Is the OptiX SDK v9.1 to v9.0 ABI diagnosis reasonable for the pod's driver/runtime behavior?

_Answer:_ Yes. The "Setup Findings" section of `docs/reports/goal2353_v2_2_rtnn_pod_baseline_2026-05-18.md` clearly documents the observed `OptiX error: Unsupported ABI version` with OptiX SDK v9.1 and its resolution by reverting to v9.0. This is a common and reasonable diagnosis for ABI compatibility issues between GPU drivers and SDKs, and the fix is appropriate. The test suite also confirms that this detail is correctly reported.

### 3. Is the RTNN CUDA 12 patch helper appropriately bounded as external-checkout compatibility work rather than an algorithmic change?

_Answer:_ Yes. The `docs/reports/goal2353_v2_2_rtnn_pod_baseline_2026-05-18.md` explicitly states that the CUDA 12 compatibility edits for RTNN are "only for the disposable external RTNN checkout," "do not change RTDL source," and "do not change RTNN's neighbor-search algorithm." This bounding is further confirmed by the `patch_rtnn_cuda12_checkout` function in `scripts/goal2348_rtnn_v2_2_external_runner.py`, which sets `claim_boundary` flags to `external_rtnn_source_patch_only: True`, `rtdl_source_changed: False`, and `algorithm_changed: False`.

### 4. Do the pod rows support the stated design conclusion that RTDL v2.2 should implement a generic `prepared_bounded_neighbor_search_3d` primitive rather than app-specific nearest-neighbor code?

_Answer:_ Yes, strongly. The "What This Shows" section in `docs/reports/goal2353_v2_2_rtnn_pod_baseline_2026-05-18.md` highlights that RTNN's measured RT traversal/search compute component is very small compared to its sorting, partitioning, batching, and data-structure work. This observation is directly supported by the detailed timings in the JSON artifacts (e.g., `sort and/or partition queries` significantly outweigh `search compute` time). This evidence indicates that a holistic, generic primitive like `prepared_bounded_neighbor_search_3d` that encapsulates these broader aspects, beyond just raw traversal calls, is necessary for effective performance in RTDL. The test suite explicitly validates this observation and the report's conclusion.

### 5. Are any report phrasings too strong, misleading, or missing important risk/debt?

_Answer:_ The report's phrasings are appropriate, precise, and avoid overstatement. The "Claim Boundary" section is clear and conservative. The conclusions drawn are well-supported by the presented evidence. Furthermore, the report proactively incorporates "Review-Driven Risk Additions" from the previous Goal2347 review, demonstrating a robust approach to identifying and addressing potential risks and technical debt. The specific mention of a "cold/pathological auto-partition artifact" for an initial slow row is also a transparent and appropriate phrasing, distinguishing it from representative performance.

---

## Verdict

`accept-with-boundary`

**Boundary:**

*   This review accepts the pod baseline for Goal2353 as a valid, bounded step forward in the RTNN v2.2 campaign.
*   The established claim boundaries (no speedup, no reproduction, no release claims) must continue to be strictly observed in subsequent work.
*   The next engineering step, implementing `prepared_bounded_neighbor_search_3d`, should prioritize encapsulating the identified dominant components (sorting, partitioning, batching) in a generic and app-agnostic manner.
