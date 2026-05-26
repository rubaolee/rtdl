# Goal2625: 3-AI Consensus On Segmented Row Stream

Date: 2026-05-26

Scope reviewed:

- `src/rtdsl/segmented_row_stream.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal2625_segmented_row_stream_test.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal2625_segmented_row_stream_contract_2026-05-26.md`

## Consensus

3-AI consensus is reached for the Goal2625 CPU/reference contract slice.

Codex conclusion:

- Accept `SEGMENTED_ROW_STREAM` / `CHUNKED_ROW_CONTINUATION` as an
  app-independent internal substrate for deterministic row pagination.
- Keep the status below stable primitive until native OptiX/Embree page
  emission and backend parity evidence exist.
- Treat capacity overflow as fail-closed exact-output failure, not truncation.

Claude review:

- Verdict: ACCEPT.
- Blocking issues: none.
- Main non-blocking hardening requested: document or enforce token/page
  alignment and add direct negative-path token tests.

Gemini review:

- Verdict: ACCEPT.
- Blocking issues: none.
- Main non-blocking boundary note: current helpers materialize rows because
  this is the CPU/reference contract; native backends should stream pages
  directly later.

## Follow-Up Edits After Review

Codex applied the non-blocking hardening that does not change the contract:

- `emit_segmented_row_page()` now rejects continuation-token offsets that do
  not align with `page_capacity`.
- Tests now cover malformed/cross-stream tokens and zero-row complete streams.

## Boundary

This consensus authorizes only the contract-first internal substrate:

```text
SEGMENTED_ROW_STREAM
alias: CHUNKED_ROW_CONTINUATION
contract: rtdl.segmented_row_stream.v1
status: internal_substrate
```

It does not authorize stable public primitive wording, native performance
claims, paper-dataset completion claims, or any app-specific native engine
logic.
