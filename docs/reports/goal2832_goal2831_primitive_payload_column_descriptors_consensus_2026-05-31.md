# Goal2832 Consensus for Goal2831 Primitive Payload Column Descriptors

Date: 2026-05-31

## Scope

Goal2832 records Codex + Gemini consensus for Goal2831:

- a generic primitive-payload column descriptor contract;
- neutral-buffer seam composition for transfer status, lifetime state, native-producer ownership, and fallback reason;
- Goal2829 same-stream partial-buffer metadata integration;
- fail-closed validation for invalid roles and native lifetimes.

## Evidence

- Codex implementation and report:
  - `docs/reports/goal2831_primitive_payload_column_descriptors_2026-05-31.md`
- Gemini independent review:
  - `docs/reviews/goal2832_gemini_review_goal2831_primitive_payload_column_descriptors_2026-05-31.md`
- Tests:
  - `tests/goal2831_primitive_payload_column_descriptor_test.py`

## Consensus Table

| Question | Consensus |
| --- | --- |
| Generic descriptor, not app API | accept |
| Neutral-buffer seam composition | accept |
| Goal2829 partial-buffer descriptor integration | accept |
| Invalid role/lifetime fail-closed behavior | accept |
| Broad public performance/release claims | not authorized |
| Next planner direction | accept-with-boundary |

## Verdict

Codex + Gemini consensus accepts Goal2831 with boundary.

The accepted claim is narrow: RTDL now has a reusable descriptor that records typed primitive payload buffers, stream ordering, fallback reason, native-producer state, and neutral-buffer lifetime metadata. The Goal2829 same-stream partial-buffer path publishes such a descriptor.

The following remain unauthorized:

- arbitrary partner execution claims;
- public speedup claims;
- broad true-zero-copy claims;
- paper reproduction claims;
- whole-app acceleration claims;
- v2.5 release claims.

## Next Goal

Build a partner-neutral continuation planner over these descriptors. It should choose CuPy/Triton/Numba only from explicit descriptor capabilities, preserve same-stream/event-ordering metadata, and fail closed with a concrete fallback reason when a requested partner cannot safely consume the descriptor.
