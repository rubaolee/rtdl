# Gemini Review: Goals4222-4225 Route Policy and Current Scale Packet

Date: 2026-06-09
Reviewer: Gemini CLI (independent reviewer)
Verdict: `accept-with-boundary`

## Executive Summary

The Goal4222-4225 chain provides robust internal evidence for the current RTDL route policies and verifies the health of the ten-app benchmark surface on NVIDIA RTX 4000 Ada. The evidence justifies the split route policy for RayJoin and the unblocked default for RT-DBSCAN. The artifacts maintain strict claim boundaries, and the test suite is comprehensive and well-aligned with the project's safety mandates.

## Question-Specific Analysis

### 1. RT-DBSCAN Profile Map (Goal4222)
The profile map in `goal4222_rtdbscan_blocked_vs_unblocked_profile_map_2026-06-09.md` clearly justifies keeping `single_pass_candidate_root_rebased` as the default. The unblocked single-pass variant outperformed the blocked variant by **3.1x to 5.2x** across all tested datasets (`clustered3d`, `road3d`, `ngsim_dense`) and scales (65k, 262k). Keeping the blocked variant as an explicit, profile-specific option is the correct engineering decision.

### 2. RayJoin Contract Scale Map (Goal4223)
The split policy for RayJoin is empirically justified by `goal4223_rayjoin_public_cdb_contract_scale_map_2026-06-09.md`. 
- **PIP one-shot** contracts favor Numba (RTDL/OptiX speedup of ~0.28x).
- **LSI and Overlay** scalar-count contracts favor RTDL/OptiX by massive margins (**25x to 314x**).
Routing bounded PIP to Numba while leveraging RTDL/OptiX for heavier segment-pair and shape-pair primitives is a sound architectural approach that respects the strengths of both backends.

### 3. Major Performance Target Map (Goal4224)
The target map in `goal4224_major_performance_target_map_after_goal4223_2026-06-09.md` and its implementation in `src/rtdsl/current_major_performance_targets.py` accurately reflect the project state. It correctly transitions route policies to `done_internal_evidence` while maintaining the necessary blocks on release actions and AMD hardware-dependent work.

### 4. Ten-App Current Scale Packet (Goal4225)
The scale packet documented in `goal4225_release_prep_current_scale_packet_2026-06-09.md` is valid health evidence. It confirms that all ten current benchmark front doors are functional on a clean pod at commit `0d9786ca`. The packet successfully avoids any overclaims (release, public speedup, whole-app, etc.) through both semantic stdout scanning and explicit test-driven verification.

### 5. Test Strength
The tests (`tests/goal4222_...`, `tests/goal4223_...`, `tests/goal4219_...`, and `tests/goal4225_...`) are highly effective. They verify:
- Clean working trees and specific source commits.
- Performance ratios that justify policy decisions.
- Absence of forbidden claim flags in both summary packets and raw stdout payloads.
- Parity between Numba and RTDL/OptiX results.

### 6. Next Engineering Target
The next major engineering target should be **AMD/HIPRT functional parity** once hardware is available. In parallel, preparation for a formal **release-grade long-run packet** (with longer durations, full artifact provenance, and multi-AI consensus) is required before any public-facing claims can be made.

## Boundary Conditions

This review **does not authorize** any of the following:
- Release action or preparation for a formal release.
- Public speedup wording or whole-app acceleration claims.
- Broad RT-core or paper-reproduction wording.
- True-zero-copy or automatic partner selection claims.
- AMD/HIPRT performance claims.
- App-specific native-engine logic.

All evidence in this chain must be treated as **internal route-policy and health verification only**.
