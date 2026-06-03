# Gemini Review - Goal3099 v2.7 Semantic Search Preview

Date: 2026-06-03
Reviewer: Gemini / Antigravity (CLI)
Verdict: `accept-with-boundary`

## Executive Summary

Goal3099 implements the optional D-8 item for the v2.7 primitive discovery workflow: a deterministic semantic search preview helper. This implementation is purely a discovery aid that maps natural user intent onto existing primitive metadata. It is NOT an ML/embedding model, does not execute code, and does not perform autonomous orchestration.

## Review Questions Evaluation

### 1. Does `find_primitive_semantic(...)` remain metadata-only and deterministic?
**Yes.** The implementation in `src/rtdsl/primitive_discovery.py` uses regex-based tokenization, a small controlled synonym table (`_SEMANTIC_SYNONYMS`), and string normalization. It scores overlap against existing primitive metadata fields (aliases, intent phrases, summaries, etc.). There are no non-deterministic components or external model dependencies.

### 2. Does it require explicit opt-in through `enable_preview=True`?
**Yes.** The `find_primitive_semantic` function enforces this check at the entry point, raising a `ValueError` if `enable_preview` is `False`. This behavior is explicitly verified in `tests/goal3099_v2_7_semantic_search_preview_test.py`.

### 3. Does the implementation avoid embeddings, network calls, LLM calls, auto partner selection, dispatch, execution, and release/performance authorization?
**Yes.** 
- All relevant constants (`PRIMITIVE_SEMANTIC_SEARCH_USES_EMBEDDINGS`, `PRIMITIVE_SEMANTIC_SEARCH_EXECUTES`, etc.) are set to `False`.
- The implementation logic is confined to text processing.
- The `PRIMITIVE_SEMANTIC_SEARCH_CLAIM_BOUNDARY` string explicitly disclaims all of the above, protecting the governance model.

### 4. Are the public exports and generated catalog boundaries accurate?
**Yes.** 
- `src/rtdsl/__init__.py` correctly exports the new surface.
- `src/rtdsl/primitive_catalog.py` includes the validation snapshot in the rendering logic.
- The generated `docs/rtdl_primitive_catalog.md` correctly reports the validation status and boundary flags.

### 5. Do the tests cover the intended learner-intent cases without overclaiming semantic correctness?
**Yes.** The test suite verifies the specific intent-mapping cases mentioned in the design report (e.g., mapping "page huge witness rows" to `continuation.segmented_chunked_rows`). It focuses on verifying that the synonym expansion works as intended without claiming broader NLP capabilities.

### 6. Should this be accepted as an optional preview closeout for D-8, or should it be deferred?
**Accept.** The implementation provides useful ergonomics for primitive discovery while strictly adhering to the "deterministic metadata-only" boundary. It successfully closes the v2.7 D-8 item as a preview feature.

## Conclusion

The implementation is well-contained, follows the established patterns for primitive discovery, and respects all architectural boundaries. The use of a controlled synonym table rather than an embedding model ensures stability and determinism for this release phase.
