# Claude Review — v2.14.3 Close-Out Plan (Goals 4982–4987)

Date: 2026-07-04
Reviewer: Claude (strict)
Under review: proposed 6-goal plan to close a clean v2.14.3 (owner-authored)

## Verdict

```text
approve_scope_and_plan_shape__with_required_adjustments
```

The scope decision is right and I endorse it: v2.14.3 = the **bounded** performance
version of the writer-free binary RayJoin operator route, **no Layer 4, not chasing the
author 0.042 s.** That is the honest, shippable line. The 6-goal shape (isolate → decide
→ matrix → correctness → docs → release) is sound. The adjustments below are not a block;
they fix one real asymmetry that would otherwise make the final matrix (Goal4984)
dishonest, plus a missing genericity proof and two ordering fixes.

## A1 (crucial) — Cold/warmup isolation must be symmetric: LSI producer, not just carrier

The plan's Goal4982 isolates the **carrier builder's ~0.69 s** cold cost. But after
Goal4977 the fresh top4 route is ~4.22 s, decomposed as:

```text
fresh writer-free hot ~4.22 s
  = LSI producer      ~2.74 s   (the dominant cost — 65% of the route)
  + downstream floor  ~1.48 s
      carrier build    0.66 s   (the 0.69 s Goal4982 targets — only ~16% of the route)
      vertex PIP       0.39 s
      reproj/sort      0.37 s
```

Both the carrier (~0.66 s Numba `njit` first-call **compile**) and the LSI producer
(~2.7 s suspected OptiX/nvcc pipeline **compile/setup**, per the midcheck's own
accounting gap and the nvcc-fallback note) are almost certainly **first-call compile /
setup costs** — the midcheck already showed the LSI stage collapses 2.69 s → 0.009 s on
replay. So they are the **same category**: amortizable compile/warmup.

**The plan warms the small one (0.69 s carrier) and is silent on the big one (2.7 s
LSI).** That cannot stand. Required:

- Goal4982 must isolate cold/warm for the **LSI producer together with the carrier**, as
  one coherent "first-call compile/setup" category.
- If Goals 4978–4981 already resolved the LSI cold cost (reusable LSI pipeline/workspace
  cache), then Goal4982 must **state that and fold it into the matrix** — do not present a
  "warm" number that has warmed the carrier but silently inherited a warmed LSI without
  saying so.
- The final matrix (Goal4984) must decompose fresh vs warm for **both**, or it is not a
  credible table.

Warming the 16% cost while leaving the 65% cost uncharacterized is exactly the kind of
favorable-boundary framing this review process exists to catch.

## A2 — Cold cost that can't be legitimately warmed stays IN the fresh headline

The phrase "或只能作为 benchmark caveat" worries me. A 0.69 s (or 2.7 s) cold cost that
is **not** legitimately eliminable by a real product warmup is **part of the fresh
number**, not a footnote. If Goal4983 concludes warmup is only a test-environment
artifact, the cold cost stays in the reported fresh route; it does not get demoted to a
caveat. Caveats explain; they don't subtract.

## A3 — The "warm" column is creditable only if app-owned warmup is a real product behavior

Goal4983's branch is the right structure: implement app-owned warmup **only if** it
corresponds to a genuine product behavior (prepare-once / query-many), else document and
do not implement. Reinforce two rules for Goal4984:

- The matrix **always shows fresh alongside warm**, never warm alone. (The whole prior
  arc's failure mode was headlining an amortized/replay number as the real cost.)
- A "warm" number is legitimate **only** under a stated, real use case where the same
  prepared pipeline serves many queries. For a one-shot overlay, fresh is the number.

## A4 — Missing: a non-RayJoin genericity proof

The architecture's core premise is "RTDL is generic; RayJoin is one app." The exact-LSI
pair-id device columns and the writer-free binary operator are being shipped as **generic
RTDL capabilities.** Yet no goal in this plan exercises that path on a **non-RayJoin
spatial shape.** Without it, "generic" is a claim, not a demonstrated property — v2.14.3
would ship a "generic operator" proven only on RayJoin. Add a minimal non-RayJoin
genericity smoke (a synthetic planar-map / point-in-polygon shape is enough) — fold it
into Goal4985's test suite. This is the difference between a generic system and a
RayJoin-shaped one that says "generic."

## A5 — Two ordering fixes

- **Correctness/regression (Goal4985) must gate the matrix (Goal4984), not follow it.**
  A performance matrix measured on a build whose 5.2/5.3/5.7 reproduction has silently
  regressed is worthless. Run regression before or concurrent with the matrix, and
  measure the matrix on the verified-correct build.
- **Separate worktree cleanup from the release call in Goal4987.** This tree has a
  documented history of many uncommitted `src/native` + `src/rtdsl` edits (the Goal4806
  142-modified-file episode). Cleanup must be its own careful step with an explicit
  `git status` audit — do not bundle a git reset into the same goal as the release
  packet and external review.

## A6 — State the author ratio on top4 or state its absence

The only measured author baseline is County×Soil (0.0421 s); v2.14.3's numbers are all
top4 County×Zipcode. Goal4984 must either measure the author overlay-compute on top4 for
an honest fresh ratio, or explicitly state "no author ratio measured on top4" — do not
leave a vacuum that a later summary fills with a flattering-sounding number. Consistent
with the scope ("not chasing 0.042 s"), a plain honest ratio or an explicit "not
measured" is fine; an implied competitiveness is not.

## Goal count

~6 stands. The adjustments mostly fold in rather than add: A1 broadens Goal4982's scope,
A4 folds into Goal4985, A5/A6 are discipline within existing goals. If Goal4983 finds
warmup is not a product strategy, ~5 is realistic, as you said. Going deeper (device-
resident / CUDA-side carrier) is correctly out of scope — that is v2.14.4.

## Bottom line

Approve the scope and the plan shape. The one thing that would make v2.14.3 dishonest is
**warming/characterizing the 0.69 s carrier while leaving the 2.7 s LSI producer cold
cost unspoken** — fix that asymmetry (A1) and the rest is good hygiene: cold stays in the
headline (A2), warm only with a real use case and always beside fresh (A3), prove
genericity once off RayJoin (A4), let correctness gate the matrix and keep cleanup
separate from release (A5), and state the top4 author ratio or its absence (A6).

## Non-authorization

Endorses only the scope and plan structure. No Layer 4, no author-speed headline, no
warm-only number, no RayJoin-specific core semantics, no public release wording until
Goal4987's external review passes on a verified-correct, cleaned tree.
