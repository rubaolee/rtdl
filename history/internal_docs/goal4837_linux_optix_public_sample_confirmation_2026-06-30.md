# Goal4837 — Linux/OptiX Public Sample Confirmation

Date: 2026-06-30

## Purpose

Confirm on the NVIDIA POD that the current repaired RTDL OptiX line still passes the RayJoin public County x Soil sample after the Goal4834 correctness repair and Goal4836 regression-harness cleanup.

This is a bounded confirmation, not a full RayJoin Section 5.7 reproduction and not a broad performance claim.

## Environment

POD:

- host: `157.157.221.29`
- port: `23132`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- driver: `550.127.05`
- memory: `20475 MiB`

RTDL worktree:

- `/workspace/rtdl_goal4817_user_smoke_20260630_102224`

Author patched source tree:

- `/workspace/RayJoin_goal4834_patched_author`

## Inputs

- left: `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
- right: `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
- answer: `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`

Answer:

- bytes: `16631243`
- sha256: `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

## Verification Commands

### Focused Linux/OptiX Tests

Command:

```bash
cd /workspace/rtdl_goal4817_user_smoke_20260630_102224
python3 -m unittest \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4373_rayjoin_cdb_point_location_route_test \
  tests.goal4374_rayjoin_exact_paper_suite_test
```

Result:

- `Ran 38 tests in 7.542s`
- `OK`

### Public Sample One-Run Confirmation

Artifact:

- `history/internal_docs/goal4837_public_sample_confirm_summary.json`

Author patched binary:

- output: `/workspace/goal4837_public_sample_confirm/author_patched.txt`
- byte-equal to answer: `true`
- bytes: `16631243`
- sha256: `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- elapsed wall: `7.811462253332138` sec

RTDL OptiX:

- output: `/workspace/goal4837_public_sample_confirm/rtdl_optix.txt`
- byte-equal to answer: `true`
- bytes: `16631243`
- sha256: `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- elapsed wall: `7.442051164805889` sec
- reported LSI emitted count: `20860`

Single-run wall ratio:

- `author_patched_wall / rtdl_wall = 1.0496383430247331x`

## Interpretation

This confirms the repaired RTDL OptiX line is byte-for-byte correct on the public County x Soil sample on NVIDIA hardware.

The single-run wall ratio is recorded for traceability only. It is not a release performance claim because:

- it is one run;
- it is one public sample, not Section 5.7 full workload;
- previous 3-run Goal4834 smoke showed RTDL did not beat the patched-author median;
- exact multi-pair paper inputs and answer files remain unavailable.

## What This Proves

- Goal4834 correctness repair survives Linux/OptiX execution.
- Author patched baseline and RTDL OptiX produce the exact public answer on County x Soil.
- The current RTDL line can proceed to harder same-source / Section 5.7 investigations.

## What This Does Not Prove

- It does not prove full Section 5.7 reproduction.
- It does not prove all eight paper pairs.
- It does not prove broad RayJoin performance.
- It does not prove RTDL beats the patched author implementation.
- It does not involve Embree.

## Next Work

Proceed to the real unresolved paper-reproduction issues:

1. County x Zipcode same-source regenerated CDB mismatch investigation.
2. Chain-level/minimal reproducer work around the earlier chain mismatch class.
3. Determine whether remaining mismatch is:
   - input/topology provenance gap,
   - deterministic author-patched baseline gap,
   - RTDL overlay continuation bug,
   - or missing exact paper input/answer evidence.

## Goal-Level Decision Audit

1. **Was I being foolish?**
   Not in this goal. The goal was bounded, correctness-first, and did not overclaim performance.

2. **What action would have made the decision foolish?**
   Promoting the single-run `1.0496x` as a performance win, or treating County x Soil as full Section 5.7.

3. **Was there another path?**
   Yes: skip this confirmation and jump to larger data. That would be less disciplined because the repaired line needed a hardware sanity check after cleanup.

4. **Can I now try a better path that solves the real problem?**
   Yes. The public sample is now stable, so the next step can focus on the unresolved same-source / exact-input gap instead of rechecking basic correctness.

## Exit Label

`completed_linux_optix_public_sample_byte_equal_confirmation__no_broad_performance_claim`
