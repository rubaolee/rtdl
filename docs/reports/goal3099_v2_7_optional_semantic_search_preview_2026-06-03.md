# Goal3099 - Optional v2.7 Semantic Primitive Search Preview

Date: 2026-06-03

## Verdict

`accept-with-boundary`

Goal3099 adds the optional D-8 preview from the v2.7 primitive discovery plan: a deterministic semantic search helper over primitive metadata. This is intentionally a discovery aid, not a planner, runtime dispatcher, embedding model, partner selector, release gate, or performance feature.

## Purpose

The D-1 through D-7 work made RTDL primitives discoverable through controlled facets, generated catalog rows, duplicate-gate metadata, composition recipes, and an advisory planner. That is the governance-correct surface, but learners often phrase intent in softer language:

- "page huge witness rows"
- "density core flags"
- "prepared scene reuse"

Goal3099 provides an opt-in preview path that maps such phrases onto the existing primitive metadata without changing the primitive hierarchy or execution model.

## Implementation

Changed files:

- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_catalog.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3099_v2_7_semantic_search_preview_test.py`

New public preview surface:

- `find_primitive_semantic(query, enable_preview=True, status=None, limit=10)`
- `validate_primitive_semantic_search()`
- `PRIMITIVE_SEMANTIC_SEARCH_PREVIEW_VERSION`
- `PRIMITIVE_SEMANTIC_SEARCH_EXECUTES`
- `PRIMITIVE_SEMANTIC_SEARCH_USES_EMBEDDINGS`
- `PRIMITIVE_SEMANTIC_SEARCH_AUTO_PARTNER_SELECTION_ALLOWED`
- `PRIMITIVE_SEMANTIC_SEARCH_CLAIM_BOUNDARY`

The helper uses deterministic tokenization plus a small controlled synonym table. It scores overlap against aliases, intent phrases, summaries, outputs, and capability tags, then returns existing `PrimitiveDiscoveryMatch` rows. It does not create new primitives and does not mutate the catalog.

## Claim Boundaries

This preview is deliberately narrow:

- It requires `enable_preview=True`; otherwise it raises a preview-only error.
- It does not execute primitives.
- It does not dispatch primitives.
- It does not use embeddings, LLM calls, network calls, or learned ranking.
- It does not auto-select partners.
- It does not authorize release readiness, public speedup wording, broad RT-core wording, true zero-copy wording, or stable-public promotion of candidate/internal primitive steps.

The generated primitive catalog now records these boundaries in its validation snapshot:

- semantic search preview validation valid: `True`
- semantic search preview executes: `False`
- semantic search preview uses embeddings: `False`
- semantic search preview auto partner selection: `False`

## Validation Examples

The preview currently validates three user-intent cases:

| Query | Top primitive |
| --- | --- |
| `page huge witness rows` | `continuation.segmented_chunked_rows` |
| `density core flags` | `traversal.fixed_radius_count_threshold` |
| `prepared scene reuse` | `execution.prepared_rt_state` |

These cases are intentionally metadata-discovery examples, not benchmark claims.

## Tests

Executed on Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3099_v2_7_semantic_search_preview_test tests.goal3094_v2_7_primitive_discovery_orchestration_closeout_test tests.goal3090_v2_7_discovery_metadata_backfill_test tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test tests.goal3084_v2_7_primitive_discovery_workflow_docs_test tests.goal3081_v2_7_advisory_planner_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test
```

Result:

```text
Ran 56 tests in 1.279s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

Syntax check:

```powershell
py -3 -m py_compile src\rtdsl\primitive_discovery.py src\rtdsl\__init__.py src\rtdsl\primitive_catalog.py tests\goal3099_v2_7_semantic_search_preview_test.py
```

Result: pass.

## Release Position

Goal3099 is a useful v2.7 learner/developer ergonomics preview, but it is not required for any release claim. It closes the optional D-8 discovery item only under a preview boundary. Any future ML/embedding-backed search, telemetry-backed ranking, or execution-coupled orchestration must be reviewed as a separate design goal.
