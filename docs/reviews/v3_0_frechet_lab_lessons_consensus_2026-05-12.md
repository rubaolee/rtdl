# Consensus: v3.0 Frechet Lab Lessons

Date: 2026-05-12
Source note: `docs/reports/v3_0_frechet_lab_lessons_after_v1_8_2026-05-12.md`

## Reviews

| Reviewer | File | Verdict |
| --- | --- | --- |
| Claude | `docs/reviews/v3_0_frechet_lab_lessons_claude_review_2026-05-12.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/v3_0_frechet_lab_lessons_gemini_review_2026-05-12.md` | `accept` |

## Consensus Result

The v3.0 Frechet lab lessons note is accepted for internal planning and review
circulation with boundary.

The boundary is important:

- The note does not authorize public claims that continuous Frechet is
  RT-core accelerated on real datasets.
- The candidate primitive names are not v3.0 delivery commitments.
- The extension mental model is exploratory, not a finalized v3.0
  specification.
- v2.0 remains the active roadmap: protocol first, PyTorch reference first,
  CuPy conformance alongside it, engine app-agnostic throughout.

## Follow-Up Applied

Claude requested local scope guards around the primitive table and extension
model. Those guards were added to the source note after the reviews:

- candidate primitive names are explicitly marked as planning ideas, not v3.0
  delivery commitments;
- the extension formula is explicitly marked as a proposed mental model, not a
  finalized specification;
- the Non-Claims section now says not to cite the candidate primitive names as
  confirmed v3.0 deliverables.

No release gate is advanced by this consensus note.
