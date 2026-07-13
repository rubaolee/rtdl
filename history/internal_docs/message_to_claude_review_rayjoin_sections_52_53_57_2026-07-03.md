# Message To Claude: Please Review RayJoin 5.2 / 5.3 / 5.7 Reproduction Summary

Claude, please review this project-level RayJoin reproduction report:

```text
history/internal_docs/rayjoin_sections_52_53_57_reproduction_report_2026-07-03.md
```

The report summarizes the current RTDL v2.14 reproduction state for:

- Section 5.2 LSI;
- Section 5.3 PIP / point-location;
- Section 5.7 polygon overlay.

Please be strict. The main thing to verify is not whether the wording is
pleasant, but whether the claims are scientifically bounded and faithful to the
evidence.

Review priorities:

1. Check whether Section 5.2 is correctly limited to LSI count evidence.
2. Check whether Section 5.3 is correctly classified as:
   - County x Zipcode: exact per-point closest-edge match;
   - Block x Water: exact per-point closest-edge match;
   - Australia Lakes x Parks representative: count-consistent only.
3. Check whether Section 5.7 is correctly bounded as:
   - two available paper-style full-stream pairs;
   - two current-source Lakes/Parks representative pairs;
   - no full hidden-input all-eight claim.
4. Check whether the report preserves the difference between available
   paper-style input and representative current-source OSM input.
5. Check whether it avoids claiming broad performance, Embree, or Numba
   correctness-critical results.
6. Check whether the public representative Section 5.7 route is honestly
   described as public LSI + public PIP + Python app output writer, without
   laundering bundled `rtdsl.rayjoin_overlay` evidence as generic-language
   evidence.
7. Check whether the suggested public wording is safe.

Requested verdict labels:

- `approve_rayjoin_52_53_57_bounded_reproduction_summary`
- `approve_with_required_amendments`
- `block_until_claim_boundaries_fixed`

If you approve with amendments or block, please list concrete required edits by
section.
