# Goal3672 Gemini Review for Goal3671 Side-Aware Owner-Face Filter

Date: 2026-06-06

## Findings:

Goal3671 successfully introduces a generic side-aware owner-face filter into the RTDL framework, addressing a critical topology-related mismatch encountered in Goal3665. The filter correctly distinguishes candidate rows where face ID alone is ambiguous by incorporating an `owner_side` parameter. The implementation maintains app-agnosticism, requiring the caller to supply explicit `(owner_face_id, owner_side)` columns. Unit tests confirm its behavior, including the intentional preservation of duplicate candidate rows to align with the RayJoin PIP row-count contract's multiplicity. Pod validation on an A5000 demonstrates that this side-aware filter effectively repairs the `47264 != 47262` full-county RayJoin PIP mismatch, achieving exact multiset parity. The report and associated artifacts are commendably cautious, explicitly disclaiming any overreaching claims regarding release readiness, default route selection, or performance benchmarks beyond the immediate scope of the fix. The primary remaining blocker for an automatic/default RayJoin route is identified as the app/data-layer derivation of owner-side columns, which is outside the native engine's responsibility.

## Review Questions:

1.  **Does the new side-aware owner-face filter stay app-agnostic, with RayJoin/CDB policy remaining caller-supplied?**
    Yes, the new side-aware owner-face filter remains app-agnostic. The RTDL engine consumes generic candidate and topology rows, and the caller explicitly supplies the `(owner_face_id, owner_side)` columns, maintaining separation of concerns as per the design. This is explicitly stated in the function docstrings, the Goal3671 report, and reinforced in Goal3602 documentation.

2.  **Is preserving duplicate candidate row multiplicity in the side-aware filter correct for the current RayJoin PIP row-count contract?**
    Yes, preserving duplicate candidate row multiplicity in the side-aware filter is explicitly stated as correct and intentional for the current RayJoin PIP row-count contract, which maintains row-stream multiplicity. This behavior is validated by unit tests and documented in the Goal3671 report and the CuPy filter's docstring.

3.  **Does the full-county pod artifact support the bounded claim that side-aware topology continuation can repair the Goal3665 `47264 != 47262` mismatch when owner-side columns are supplied?**
    Yes, the full-county pod artifact (`full_county_side_aware_route_probe.json`) provides strong evidence that the side-aware topology continuation successfully repairs the `47264 != 47262` mismatch, achieving multiset parity with the exact row count by correctly filtering the identified extra rows `(893, 16312)` and `(894, 16312)`. This is validated by unit tests.

4.  **Does the report avoid overclaiming automatic/default route selection, release readiness, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy?**
    Yes, the report and associated artifacts are very conservative and explicitly avoid overclaiming on automatic/default route selection, release readiness, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy. The `claim_boundary` flags in the pod artifact are all set to `false`, and the report includes clear boundary statements disallowing such claims.

5.  **What is the next major engineering step: owner-side derivation, native/device lowering of the side-aware filter, fused exact closed-shape count, or something else?**
    The next major engineering step is the caller-side derivation of owner-side columns. This is identified as app/data-layer policy and is the primary blocker for enabling an automatic/default RayJoin route. Native/device lowering of the side-aware filter (which is already implemented in CuPy) and fused exact closed-shape count are not identified as the *immediate* next major blocking step.

## Expected Verdict:

`accept`

## Recommendations:

1.  **Prioritize Owner-Side Derivation:** Expedite the definition, review, and validation of the app/data-layer derivation of owner-side columns. This is the critical path to promoting this side-aware repair capability into an automatic or default RayJoin route.
2.  **Documentation of Caller Policy:** Ensure comprehensive documentation and examples are developed for callers on how to correctly supply `(owner_face_id, owner_side)` columns, particularly for RayJoin/CDB use cases.
3.  **Performance Baseline for Derivation:** Once owner-side derivation is defined, establish performance baselines for this derivation process to identify any potential bottlenecks before full integration into a default route.
4.  **Future Fused Primitives:** Continue to explore the long-term goal of a more compact, fused native scalar-count path or another generic closed-shape predicate-count primitive to reduce per-request traversal overhead for scalar-count-only PIP, as noted in `future_version_to_do_list.md`. This is a separate, longer-term optimization, not a blocker for the current goal.