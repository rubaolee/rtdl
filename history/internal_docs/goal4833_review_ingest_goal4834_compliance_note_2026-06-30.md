# Goal4833 Claude Review Ingest and Goal4834 Compliance Note

Date: 2026-06-30

Source review:

- `history/internal_docs/claude_goal4833_method_reset_review_2026-06-30.md`

## What This Review Adds

The Claude Goal4833 review is now treated as a standing method constraint for
the RayJoin product-repair line.  Its important rule is not merely "write more
tests"; it is:

> A core semantics change is legitimate only when a minimal synthetic test
> derived from the paper/author contract shows the old behavior violated the
> contract and the new behavior matches it.  "It made RayJoin pass" is not a
> valid justification for changing RTDL core.

This rule controls all future work that touches `src/native/**` or shared RTDL
runtime semantics.

## Compliance Crosswalk

| Claude amendment | Current status after Goal4834 |
| --- | --- |
| AM1: synthetic contract test gates core repair | Satisfied for the directed point-location SoS comparator repaired in Goal4834. `tests/goal4834_rayjoin_sos_synthetic_contract_test.py` was run locally and on POD before public-sample evidence was used. |
| AM2: do not grandfather unjustified changes | Partially satisfied. The SoS comparator was re-derived and tested. However, the current `src/rtdsl/rayjoin_overlay.py` diff still contains broader historical changes around scaled coordinates, sort keys, rational midpoint handling, and non-finite filtering. Goal4834's approval does **not** automatically justify all of those changes. |
| AM3: core change requires v2.14-wide regression gate | Outstanding. Goal4834 proved the public County x Soil sample and focused tests, but did not run the full v2.14 app/benchmark regression matrix. |
| AM4: add chain-30138 and rational-vs-float synthetic tests | Partially satisfied. A rational/scaled-coordinate midpoint synthetic test exists in `tests/goal4374_rayjoin_exact_paper_suite_test.py`. The chain-30138 minimal reproducer is still outstanding unless a later file explicitly records it. |

## Important Local Audit Finding

Current diff inspection shows `src/rtdsl/rayjoin_overlay.py` contains more than
the per-map midpoint-face repair:

- author-style coordinate scaling helpers;
- rational scaled intersection fields;
- scaled sort-key logic;
- rational midpoint projection;
- non-finite midpoint filtering.

These may be useful product repairs, but they must not be silently inherited as
"already approved" by Goal4834.  They need one of the following outcomes:

1. a contract-derived synthetic test and review approval;
2. explicit classification as historical/experimental work not yet approved;
3. reversion before any release-facing claim.

## Operational Rule Going Forward

Before another broad RayJoin or v2.14 release-facing claim:

- run the full v2.14 regression/benchmark matrix or explicitly record why it is
  deferred;
- audit each `rayjoin_overlay.py` behavioral change against a paper/source
  contract or synthetic test;
- do not use public-sample byte equality alone to justify broader core/runtime
  behavior changes.
