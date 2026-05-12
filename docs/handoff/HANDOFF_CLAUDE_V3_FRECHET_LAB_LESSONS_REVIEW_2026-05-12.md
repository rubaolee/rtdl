# Handoff: Claude Review Of v3.0 Frechet Lab Lessons

Please independently review:

```text
docs/reports/v3_0_frechet_lab_lessons_after_v1_8_2026-05-12.md
```

Context:

- v1.8 shipped as Python+RTDL with an app-agnostic native engine.
- v2.0 remains the active roadmap: protocol first, PyTorch reference first,
  CuPy conformance alongside it, engine app-agnostic throughout.
- The Frechet lab was a learner test, not a release target.
- It showed RTDL+Python can beat pure Python on synthetic cases, but not
  optimized C++ on the real GeoLife trajectory pair tested.
- Existing related concept/review:
  - `docs/reports/v3_0_custom_engine_extensions_concept.md`
  - `docs/reviews/v3_0_custom_engine_extensions_concept_claude_analysis_2026-05-11.md`

Review questions:

1. Does the note keep v2.0 focus intact, or does it accidentally pull roadmap
   attention toward v3.0 too early?
2. Are the proposed future primitives named and framed app-agnostically?
3. Does the note avoid overclaiming real-dataset continuous Frechet
   acceleration?
4. Does it correctly refine the old v3.0 custom-engine-extension idea away from
   the oversimple "PCIe slot" metaphor?
5. Are the non-claims strong enough for public roadmap safety?

Write the review to:

```text
docs/reviews/v3_0_frechet_lab_lessons_claude_review_2026-05-12.md
```

Required:

- State reviewer identity as Claude.
- State whether this review is independent from Codex authoring.
- Use one verdict exactly: `accept`, `accept-with-boundary`,
  `needs-more-evidence`, or `reject`.
- Do not edit source code.
- Do not make a consensus file.
- Codex+Codex is invalid consensus; this must be a Claude review.
