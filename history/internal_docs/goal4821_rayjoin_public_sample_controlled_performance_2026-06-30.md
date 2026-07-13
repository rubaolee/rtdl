# Goal4821 — RayJoin Public Sample Controlled Performance Smoke

Date: 2026-06-30

Status: `approved_bounded_public_sample_performance_smoke`

## Purpose

Goal4820 repaired the correctness path for the RayJoin author public sample.
Goal4821 measures a narrow, correctness-gated performance smoke on the same
sample:

- input pair: County x Soil public sample;
- author answer must match byte-for-byte;
- author binary and RTDL output are both checked by SHA256 on every run;
- result is a bounded public-sample measurement only.

This goal does **not** claim full Section 5.7 reproduction, full eight-pair
coverage, or broad RTDL performance.

## Environment

POD:

- `root@157.157.221.29 -p 23132`

RTDL repaired checkout:

- `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- OptiX library:
  `/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so`

Author source:

- clean worktree:
  `/workspace/RayJoin_goal4821_clean`
- author HEAD:
  `02bf6220d6d20b04af77ee20364eced75cc029c9`

Inputs:

- left:
  `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
- right:
  `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
- answer:
  `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`
- answer SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

## Author Build Note

A pristine author worktree build failed under the current CUDA 12.8 / GCC 13
environment due to build-compatibility issues:

- CUDA/NVTX header redefinition;
- `std::unordered_map<double2, ...>` lacking portable hash/equality support.

The performance smoke therefore uses an author **clean-compat** binary built
from the clean worktree plus a minimal compatibility patch:

- no-op NVTX marker header;
- explicit `double2` hash/equality for the output-chain point map.

No author algorithm, PIP, LSI, RT traversal, or overlay logic was changed.

Author clean-compat binary:

- path: `/workspace/RayJoin_goal4821_clean/release/bin/polyover_exec`
- SHA256:
  `cc7bccbb2409a0c7fe8f8cf2ad4090ece63cf1e3c44c7852fd2d470de1dbc0bc`

Compatibility patch artifact:

- `history/internal_docs/goal4820_artifacts_2026-06-30/goal4821_author_clean_compat.patch`

## Result

Artifact:

- `history/internal_docs/goal4820_artifacts_2026-06-30/goal4821_perf_clean_compat_summary.json`

All runs were byte-equal to the author answer:

- author clean-compat binary: 3/3 byte-equal
- repaired RTDL OptiX: 3/3 byte-equal

Median wall-clock:

| Route | Median wall seconds | Correctness |
| --- | ---: | --- |
| Author clean-compat binary | `7.702967159450054` | 3/3 byte-equal |
| Repaired RTDL OptiX helper | `4.510876469314098` | 3/3 byte-equal |

Bounded speed ratio on this public sample:

- `author_wall / rtdl_wall = 1.7076431181058986x`

## Claim Boundary

This is a narrow correctness-gated public-sample smoke:

- County x Soil only;
- same public input pair;
- full output bytes validated;
- wall-clock includes Python/author process/app output work;
- author binary is clean-compat, not pristine build;
- not full Section 5.7;
- not an eight-pair paper claim;
- not a broad RTDL performance claim.

## Next Work

The next goal should decide one of two paths:

1. Expand cautiously to more Section 5.7 pairs only when exact author inputs and
   answer files are available.
2. If exact inputs/answers are not available, keep the claim at this bounded
   public-sample level and document the remaining input gap.

## External Review

Antigravity approved this goal with verdict:

`approve_goal4821_bounded_public_sample_performance_smoke`

Review record:

- `history/internal_docs/antigravity_goal4821_rayjoin_public_sample_controlled_performance_review_2026-06-30.md`

The authorized next step is an exact-input/ground-truth availability audit for
additional Section 5.7 pairs before any further performance run.
