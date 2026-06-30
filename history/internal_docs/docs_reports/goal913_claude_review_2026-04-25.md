# Goal 913 Claude Review

Date: 2026-04-25

Verdict: ACCEPT

Claude reviewed only the Goal913 files, avoiding the unrelated large dirty JSON
files in the working tree.

Key findings:

- `visibility_pair_rows(...)` correctly preserves explicit observer-target
  candidate-edge semantics and avoids the Cartesian `visibility_rows(...)`
  behavior that caused the RTX graph artifact to emit 8,000,000 rows instead of
  80,000.
- The graph gate now uses summary-mode app calls when validating summary-mode
  analytic parity, so BFS and triangle-count row digests no longer hash
  intentionally omitted row payloads.
- Jaccard candidate diagnostics are useful because they expose raw candidate
  counts outside the canonical parity digest, which intentionally ignores
  `candidate_row_count`.
- The cloud rerun plan is honest: it targets only the failed graph and Jaccard
  gates and does not authorize public RTX speedup claims.

Minor note:

- In full-reference mode, the Jaccard diagnostic baseline may come from CPU
  refined rows rather than analytic positive candidate count. The documented
  next cloud rerun uses `analytic_summary`, so the expected baseline is the
  intended `3 * copies` candidate count.

Blocking issues: none.
