# Goal1740 v1.8 Public Docs Boundary Alignment

## Verdict

`docs_boundary_aligned_for_v1_8_preparation`

This goal updates the highest-risk current public documentation pages so they no longer read as though current `main` is only the older v1.6 release boundary. The edits preserve the released v1.6 historical boundary while making room for the later v1.6.11/v1.8-preparation evidence chain.

## Files Updated

- `docs/current_architecture.md`
- `docs/current_main_support_matrix.md`
- `docs/performance_model.md`
- root `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `tests/goal1740_v1_8_public_docs_boundary_alignment_test.py`

## Alignment Rules Applied

- v1.6 remains the current released public tag boundary.
- Current `main` is described as containing later v1.6.11/v1.8-preparation evidence.
- The tracked release native surface may be described as migrated toward app-agnostic ABI terminology under the v1.7/v1.8 gates.
- v1.8 is still pending explicit release authorization, packaging/install boundary choice, final documentation alignment, test-matrix definition, and final v1.8 consensus.
- v1.8 remains Python+RTDL productization only.
- v2.0 remains Python+partner+RTDL.

## Blocked Claims Preserved

The updated docs continue to block:

- whole-application speedup claims
- broad backend speedup claims
- arbitrary RTX acceleration claims
- partner-readiness claims
- universal partner zero-copy claims
- claims that choosing a backend flag alone proves acceleration

## Validation

The focused docs/audit gate passed locally:

```text
py -3 -m unittest tests.goal1740_v1_8_public_docs_boundary_alignment_test tests.goal1737_v1_8_python_rtdl_gap_audit_test tests.goal1736_v1_6_11_commit_ready_inventory_test

Ran 10 tests in 0.004s
OK
```

The Python launcher still emitted the existing local warning:

```text
Could not find platform independent libraries <prefix>
```

That warning did not prevent the tests from running or passing.

## Remaining Documentation Work

This goal aligns the current highest-risk public docs and front-door indexes. Before v1.8 release, a final documentation sweep should still cover any v1.8 release package files created after the packaging/install decision.

## Boundary

This is documentation alignment for v1.8 preparation. It is not a v1.8 release packet, not a tag authorization, and not a packaging/install decision.
