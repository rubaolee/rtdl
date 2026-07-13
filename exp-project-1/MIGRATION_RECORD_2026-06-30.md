# exp-project-1 Migration Record

Date: 2026-06-30

Decision: restore the public repository root to the RTDL v2.14 line and isolate all post-v2.14 V3/V4 exploration work under `exp-project-1/`.

## Public Root Policy

- The repository root is the public v2.14 project surface.
- V3/V4 work after v2.14 is not part of the public root and is treated as exploratory project work.
- The exploratory project is preserved here, not deleted.

## Archived Inputs

- The tracked-source snapshot of the pre-migration HEAD is recoverable from git:
  - branch: `codex/v4-tier2-section8`
  - HEAD at archive time: `35e295a83`
  - local-only `current-head-source.tar` was intentionally ignored and was removed during cleanup on 2026-07-04 because the git commit is the durable source of truth.
- `untracked-current/` contains untracked reports, reviews, and Goal4806 material present before the root was restored.

## Restore Target

- Public restore tag: `v2.14`
- `v2.14` commit: `03a3201c04d391f8f08148da14445d4cd1b1149c`
- Root tracked files were restored from `v2.14`.
- Two intentional public-front-door corrections were applied after restore:
  - `README.md` now says v2.14 instead of the stale v2.13 wording in the tag.
  - `scripts/rtdl_source_tree_doctor.py` now checks v2.14 and the v2.14 release package instead of the stale v2.13 marker.

## Verification

- `git diff --name-only v2.14 -- .` reported only the intentional v2.14 front-door consistency changes after restore.
- `git ls-files --others --exclude-standard | rg -v "^exp-project-1/"` reported no files.
- `VERSION` reads `v2.14`.
- `PYTHONPATH=src:. py -3 scripts/rtdl_source_tree_doctor.py` passed core checks with optional native/partner warnings only.
- `PYTHONPATH=src:. py -3 -m unittest tests.goal4386_v2_14_final_closeout_test tests.goal4380_v2_14_benchmark_run_plan_test` passed 10 tests.

## Goal-Level Decision Audit

1. Was the decision foolish?

No. The corrective decision is sound: keeping V3/V4 at the public front door created confusion and made unsupported claims look like current product facts.

2. What prior actions made the earlier state foolish?

The public tree allowed V3/V4 release, tutorial, review, and benchmark material to sit beside current user-facing material. That blurred product truth, experiment truth, and internal review truth.

3. Was there another path that avoided locking into the wrong idea?

Yes. The safer path is exactly this migration: keep v2.14 as the public product line, preserve the later work as an explicit experiment, and require future promotion to happen deliberately rather than by file drift.

4. Can we now try a different path that solves the real problem?

Yes. The root can now be audited and improved as a v2.14 product surface. V3/V4 ideas can continue only as `exp-project-1` exploration until they earn promotion through evidence and review.
