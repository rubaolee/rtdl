# Claude Review — RTDL v2.14.3 Full Technical Release-Stage Review

Date: 2026-07-04
Reviewer: Claude (strict)
Scope: technical report, Goals 4983/4984/4985/4987, helmholtz review, public README +
release packet, native OptiX edits, MAX_ITER test change, genericity tests.

## Primary verdict

```text
approve_technical_packet_but_require_release_staging_cleanup
```

The technical packet is coherent, honestly bounded, and adopts every amendment from the
prior close-out-plan review: the ~2.7 s LSI producer stays **in** the fresh headline
(Goal4983 `warmup_not_product_strategy`), warm/repeated is always shown beside fresh and
never headlined alone, the `0.000000 s` LSI diagnostic is rejected, no top4 author ratio
is invented, correctness (Goal4984) gates the matrix (Goal4985), and cleanup (Goal4987)
was audit-only (removed `__pycache__`, deleted no evidence). I verified the risky items
against the files rather than trusting the prose, and they hold up. **No P0 blocker.**

But this is a "cleanup-required" approval, not a clean-approve, because the packet makes
one architectural claim it does not fully earn (core genericity), rests one release-gating
property on a locally-skipped runtime test, assembles the performance matrix from
separate runs, and leaves 103 internal docs one staging mistake away from shipping. These
are P1s to resolve **at staging**, before any human push — not reasons to rework the
engineering.

## What I verified (not just restated)

- **MAX_ITER 5→0 in `goal4374` is a legitimate sync, not a correctness weakening.** The
  product default in `src/rtdsl/rayjoin_overlay.py` is `"0"`; `goal4894` independently
  locks it (native `rayjoin_cdb_group_max_iter_from_env()` returns 0, group mode
  `FineGrained`, and asserts the auto-env sets MAX_ITER `"0"` and **not** `"5"`). The
  `goal4374` edit updated one stale env-contract assertion (line 680) to `"0"`; the
  paper byte-equality assertions are elsewhere and the 54-test suite re-ran green. This
  is aligning a stale historical test to the current, separately-locked contract. ✓
- **The non-RayJoin genericity test is real, not superficial.**
  `goal4948_non_rayjoin_hit_stream_numba_genericity_test` reads the actual
  `device_column_row_buffer_from_hit_stream_handoff` body and asserts it contains none of
  `rayjoin/polygon/overlay/output_chain/authorofficial`, and the runtime subtest exercises
  a genuinely non-RayJoin ray/triangle 3D hit-stream through the same row-buffer path. ✓
  **Caveat (P1 below): the runtime half is the skipped subtest locally.**
- **Public surface is clean and correctly bounded.** README + release packet carry no goal
  IDs, reviewer names, `verdict`/`call_for_review`/`2.04x`, or V3/V4 language; they lead
  with fresh `4.22 s`, mark repeated `3.62–3.67 s` secondary, mark prepared replay
  diagnostic-only, state "no top4 author denominator," and disclose the AuthorOfficial
  comparator honestly (duplicate-half-edge = RTDL-defined deterministic contract, not raw
  author behavior). ✓
- **The new v2.14.3 native surface is generically named** (`segment_pair` / `pair_id`
  exact-LSI symbols), consistent with the genericity red-line.

## P1 — Required before human release staging

### P1-1. The "core is fully generic" claim is overstated — bound it
The technical report asserts "不能把 RayJoin overlay 语义藏进 RTDL core" and "RTDL core
不应该出现 app-specific 语义." But the core package still carries app identity:
- `src/rtdsl/rayjoin_overlay.py` — a RayJoin-specific overlay module living **inside the
  rtdsl package**. (v2.14.3's binary route correctly does not import it, and the public
  scripts avoid it — but the correctness suite `goal4374` does import it, and it ships in
  core.)
- Native `src/native/optix/rtdl_optix_prelude.h` carries `RtdlRayjoinCdbSegment`,
  `RtdlRayjoinCdbPointLocationRow`, `RtdlRayjoinCdbScaledPoint`,
  `rtdl_optix_prepare_rayjoin_cdb_point_location_2d`, and internal `RayjoinCdbGroupMode` /
  `rayjoin_cdb_group_max_iter_from_env()` — RayJoin-**named** core symbols (typedef'd to
  generic `RtdlDirectedSegment*` aliases).

The *semantics* are generic (directed-segment point-location / planar-map LSI); the
**naming and packaging still embed the app identity**. This is pre-existing legacy, not a
v2.14.3 regression, and it does not leak to the public surface (leak scan covers
README/docs; these names are internal). But the report's absolute claim must be made
precise: "the new v2.14.3 primitives and the public surface are generic; legacy
`rayjoin_cdb`-named point-location symbols and a bundled `rtdsl.rayjoin_overlay` helper
remain in-tree pending rename/relocation." Do not ship the unqualified "core is generic"
sentence next to a core that literally contains `Rayjoin` symbols.

### P1-2. Non-RayJoin genericity is proven statically but not at runtime locally
The single skipped subtest **is** the non-RayJoin hit-stream GPU-runtime execution
(`goal4948` runtime half). So "runtime genericity" rests on "prior POD evidence" that the
gate does not cite. For a release that ships these as **generic** RTDL capabilities,
require one **cited POD run** of the non-RayJoin hit-stream runtime (ray/triangle path),
or explicitly bound the claim to "static genericity + RayJoin runtime; non-RayJoin runtime
last verified on POD <ref>." A generic claim whose only runtime proof is the app it's
trying to be independent of is not yet a proven generic runtime.

### P1-3. The performance matrix is stitched from separate runs/PODs — disclose or re-run
`7.851 s` (normal), `5.904 s` (exact-LSI), `4.220 s` (fast pack), `3.669 s` (repeated)
come from different goals and likely different PODs. The same "public rows / normal"
baseline was `7.851 s` in one goal and `9.387 s` in another — ~20% run/POD variance, which
is larger than some intermediate sub-steps being credited. The matrix uses the **lower**
baseline (7.851), so the `1.86x` is conservative, not inflated — good — but a "final
performance matrix" should either (a) be produced in **one same-POD session** running
normal → exact-LSI → fast-pack back-to-back, or (b) explicitly label the rows as
assembled-from-separate-runs with a ±~20% baseline-variance caveat and treat `1.86x` as a
single-run point estimate, not a firm factor.

### P1-4. The 103 untracked `history/internal_docs/` files are a staging landmine
The leak scan (correctly) covered only `README.md docs examples/current tutorials/current`
and the app README — **not** `history/internal_docs/`, which contains exactly the
forbidden language (goal IDs, `Claude`/`Gemini`/`Codex`, `call_for_review`, `verdict`,
`2.04x`, cold-vs-warm internal numbers). These 103 files are "project state awaiting
staging," but the staging step **must** guarantee they never enter a public release
artifact/branch. Make this an explicit, checked gate in the staging plan, not an
afterthought — one `git add .` on the wrong branch ships the entire internal review trail.

## P2 — Should fix, not blocking

- **P2-1.** Rename the legacy `rayjoin_cdb`-named native symbols to their generic typedef
  names (and consider relocating `rtdsl.rayjoin_overlay` to an app namespace) in a future
  goal, so the package matches the "generic core" claim.
- **P2-2.** The dirty-tree count was already stale once (helmholtz caught 117→116 / 125→124).
  Re-audit `git status` immediately before staging so the release notes match reality.
- **P2-3.** The plan's Goal4984 asked for a `v2.14.1 / v2.14.2 / v2.14.3` version matrix;
  the delivered matrix is a route-evolution matrix (normal → exact-LSI → fast-pack). The
  route matrix is more informative, but note the deviation so no reader expects per-version
  rows that aren't there.

## Answers to the review questions (condensed)

1. Separates RTDL-generic from RayJoin-app responsibilities? **Mostly** — semantics and
   public surface yes; core naming/packaging still embeds app identity (P1-1).
2. Primitives genuinely generic, not RayJoin-in-disguise? **Semantically yes; new symbols
   generically named; legacy point-location symbols carry a `rayjoin_cdb` name (P1-1).**
3. Writer-free framing architecturally sound, not a favorable redefinition? **Sound** — a
   pipeline consumes binary/columnar rows, not a text file; and the text route is retained
   as the correctness anchor, so it is a reframe, not a benchmark dodge.
4. Text route treated as correctness anchor, not perf route? **Yes.**
5. Non-RayJoin genericity sufficient given the GPU skip? **Static yes; runtime not proven
   locally — P1-2.**
6. `7.851 → 4.220` supported? **Yes, as a conservative single-run estimate — firm it up per P1-3.**
7. `3.62–3.67 s` correctly bounded as secondary? **Yes** — never headlined, LSI included, warm-carrier labeled.
8. Correct to report no top4 author ratio? **Yes** — honest absence; refuses to reuse 0.0421 s.
9. `0.000000 s` LSI diagnostic correctly rejected? **Yes.**
10. Bottleneck = LSI producer setup/ensure (not launch/carrier/writer)? **Yes** — decomposed
    (grouped-range ensure ~1.03 s, scaled-cache ~0.69 s, exact-pipeline ~0.52 s, split-kernel
    ~0.43 s, native launch ~0.0023 s).
11. Any perf claim still misleading? **Only the stitched-matrix single-run framing (P1-3);
    otherwise honestly bounded.**
12. Correctness gates adequate? **Yes** — 85 local tests, gate before matrix, one legit sync.
13. MAX_ITER 5→0 valid? **Yes — verified against the current locked contract.**
14. New tests cover the risky changes? **Yes** — fast pack (parity + ABI), exact LSI device
    columns, point-location device faces, carrier decomposition, side-order no-go, genericity.
15. Skipped GPU subtest acceptable? **For static staging yes; require a cited POD run for the
    non-RayJoin runtime (P1-2) before claiming runtime genericity.**
16–18. Public docs explain the binary route + boundaries, avoid IDs/reviewers/stale-V3V4,
    avoid author-parity/broad-speedup/warm-only? **Yes on all.**
19. Technical report clear for a stakeholder? **Yes** — with the P1-1 genericity wording fix.
20–21. Dirty-tree acceptable / artifacts appropriate? **As project state yes; enforce P1-4
    (internal_docs must not ship) and P2-2 (recount).**
22. Ready for human release staging? **Yes, after the P1 cleanup items — hence the
    cleanup-required verdict, not a block.**

## Bottom line

The engineering and the honesty are release-grade: fresh keeps its LSI, warm never
masquerades as fresh, no author ratio is faked, correctness gates the matrix, and the
public surface is clean. Hold staging only for cleanup, not rework: bound the "generic
core" claim to match a tree that still contains `Rayjoin` symbols (P1-1), give the
non-RayJoin runtime one cited POD run (P1-2), disclose or same-POD re-run the stitched
matrix (P1-3), and gate the 103 internal docs out of any public artifact (P1-4). Fix those
four at staging and v2.14.3 is a clean, honestly bounded release.

## Non-authorization
This review authorizes proceeding to human release **staging** with the P1 cleanup, not a
public push. No author-parity, no warm-only headline, no broad RTDL speedup, no top4 author
ratio, no "true device-resident overlay complete," no Layer 4, and no unqualified "RTDL
core is generic" while `rtdsl.rayjoin_overlay` and `rayjoin_cdb` core symbols remain in-tree.
