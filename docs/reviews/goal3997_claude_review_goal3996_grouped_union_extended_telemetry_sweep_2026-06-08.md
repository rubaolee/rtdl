# Claude Review: Goal3996 Grouped-Union Extended Telemetry Sweep

Date: 2026-06-08
Reviewer: Claude (independent read-only review)

## Verdict

`accept-with-boundary`

## Scope

Read directly from the workspace:

- `docs/reports/goal3996_grouped_union_extended_telemetry_sweep_2026-06-08.md`
- `docs/reports/goal3996_grouped_union_extended_telemetry_sweep_pod.json` (full sweep, all three point counts and all four mode variants, cross-checked numerically)
- `scripts/goal3996_grouped_union_extended_telemetry_sweep_pod.py`
- `tests/goal3996_grouped_union_extended_telemetry_sweep_test.py`
- `docs/research/future_version_to_do_list.md` ("Dense Fixed-Radius Grouped Union" section, lines 91-127)
- `docs/reports/goal3990_dense_fixed_radius_grouped_union_design_2026-06-08.md`
- `docs/reports/goal3992_grouped_union_extended_telemetry_2026-06-08.md`
- `docs/reviews/goal3994_claude_review_goal3992_grouped_union_extended_telemetry_2026-06-08.md`

I independently recomputed every "ratio vs default" cell in the report's Native Median Summary table from the raw `median_native_elapsed_sec` values in the pod JSON (all 12 rows, three point counts × four variants) and they all match to the displayed precision (e.g. `65,536`: `0.335920/0.289941 = 1.159x`, `0.287766/0.289941 = 0.992x`, `0.294877/0.289941 = 1.017x`; `16,384`: `1.170x`, `0.942x`, `0.977x`; `4,096`: `1.306x`, `1.000x`, `1.059x`). I also confirmed the headline `65,536`-point telemetry counters (`892,847,094` radius candidates, `891,004,699` same-root culled, `0` direct hits, `1,842,395` reported, `1,310,439`/`65,535` atomic attempts/successes) against `last_telemetry` in the JSON at line 1854.

## Findings By Question

**1. Does the Goal3996 artifact support the conclusion that simple grouped-union mode toggles are exhausted?**

Yes, for the tested profile/scale. The sweep covers all four combinations of `same_root_culling` × `direct_side_effect` at `4,096`/`16,384`/`65,536` points, repeated three times each (`tests/...test.py:35-43` confirms exactly these four labels are present). The native-median data is internally consistent and the pattern is uniform across all three sizes:

- Disabling same-root culling is slower at every size (`1.306x`, `1.170x`, `1.159x`), and the telemetry shows why — `same_root_culled_candidate_hits` collapses from ~99% of radius candidates to `0` and `reported_intersection_candidates` balloons to the full radius-candidate count, so the kernel reports (and the host receives) every candidate instead of culling almost all of them before `__anyhit__`.
- Enabling direct side effects is roughly neutral-to-marginally-faster under instrumentation (`1.000x`/`0.942x`/`0.992x` with same-root on; `1.059x`/`0.977x`/`1.017x` with same-root off), i.e. within noise at the largest measured size, not a durable win.

This is a clean, internally consistent A/B/C/D matrix, and it extends (rather than contradicts) the prior Goal3987/Goal3989 findings recorded in the to-do list (lines 93-105), which already ruled out blocked ranges, direct side effects, and disabled same-root culling as wins on this same profile. The "exhausted" framing is therefore well supported *for the `clustered3d` profile at `radius=0.5` and the measured scales* — see the boundary note below about making that scope explicit.

**2. Is the interpretation correct that dense candidate enumeration/root-read work, not successful union atomics alone, is the next bottleneck?**

Yes. The `65,536`-point default-mode row shows `892.8M` radius-qualified candidates (`telemetry[4]`) against only `65,535` successful unions (`telemetry[1]`), a ratio of about `13,625:1`, while parent atomic attempts are only `1,310,439` (about `20:1` against successes — consistent with Goal3989's "~1.24 attempts per point" finding once you note `1,310,439/65,536 ≈ 20`, dominated here by extended-telemetry instrumentation overhead rather than the underlying union-find traffic Goal3989 measured). The dominant volume by a wide margin is candidate enumeration and same-root culling reads (`telemetry[4]` and `telemetry[5]`, both in the hundreds of millions), not the relatively modest atomic-union traffic. The test `test_large_row_shows_candidate_work_dominates_unions` codifies exactly this shape (`telemetry[4] > telemetry[1] * 10_000` and `telemetry[5] > telemetry[7]`), and both assertions hold comfortably in the artifact. The interpretation is a direct, justified reading of the counters Goal3992 added and Goal3994 already validated as correctly wired.

**3. Does the report preserve the app-agnostic native-engine boundary and avoid DBSCAN-specific ABI direction?**

Yes. The only DBSCAN-flavored language in the report is the single contextual sentence in the Verdict summary explaining *why* the sweep was run ("decide whether the next RT-DBSCAN improvement can come from a simple execution-mode toggle..."), which is motivation/context, not engine-vocabulary direction. The "next meaningful improvement" bullets (lines 51-56) and the Boundary section (line 60) speak entirely in generic primitive terms — "generic dense grouped-union primitive", "dense fixed-radius candidate work", "convergence/staleness/status metadata", "exact same-contract parity" — with no clustering/epsilon/min-points/app-label vocabulary. `claim_boundary.dbscan_native_abi_added: false` is asserted in the JSON, and the contract test explicitly checks `assertNotIn("DBSCAN native ABI", report)`. This matches the to-do list's own boundary framing for this work item (lines 119-122: "It must not encode DBSCAN, clustering, epsilon/min-points policy, or application-specific labels in native ABI names").

**4. Does the report avoid public speedup/release/whole-app/zero-copy overclaims?**

Yes. The "Native Median Summary" section opens with an explicit disclaimer that the timings are "diagnostic telemetry timings" that "include extended telemetry atomics and must not be used as public speedup evidence" (line 26). The dedicated Boundary section (line 60) disclaims release authorization, public/broad-RT-core/whole-app speedup wording, paper reproduction, true-zero-copy wording, automatic partner/backend selection, and app-specific native-engine logic — mirroring the JSON's `claim_boundary` block (`performance_claim_authorized: false`, `release_authorized: false`, `telemetry_is_diagnostic: true`, `dbscan_native_abi_added: false`) and each per-sample `metadata` entry (`paper_speedup_claim_authorized: false`, `true_zero_copy_authorized: false`, `v2_0_release_authorized: false`). I found no place where the report uses the per-mode ratios or absolute timings to assert a production speedup or readiness claim — they are used solely to compare modes against each other under identical instrumentation, which is the correct apples-to-apples framing for this kind of diagnostic A/B.

**5. Are there any missing validation requirements before implementing the next generic dense grouped-union primitive?**

The report's own "next meaningful improvement" bullet list (lines 51-56) is reasonable but narrower than what the to-do list separately records as the acceptance bar for this work item. The to-do list (lines 123-127) additionally calls out: deterministic component-root policy, dense *and sparse* pod profiles (the report only used `clustered3d`), and independent/external review, plus "treat performance results as profile-bound until broader datasets are measured." None of these are missing from the project's overall plan — they live in `future_version_to_do_list.md`, which this same goal updated (lines 106-112) — but a reader of the Goal3996 report alone would see a slightly thinner "what's required next" list than the to-do list's full acceptance criteria. This is not a defect in Goal3996 (it is a diagnostic sweep, not a primitive-design doc — that is Goal3990's job), but it is worth noting that the to-do list, not the report, is the authoritative place those fuller acceptance criteria live.

## Minor Observations (non-blocking)

- The report's "The simple mode switches are exhausted" framing (line 45) is stated without an explicit profile/scale qualifier in that sentence, even though the Pod Setup section directly above it documents `profile: clustered3d`, `radius: 0.5`, and the three measured sizes. Prior goals in this chain (e.g. Goal3987, per the to-do list) scoped their "ruled out" language to "the current `clustered3d` scale profile." A one-clause addition such as "...are exhausted on this profile/scale" would make the boundary self-contained without requiring the reader to cross-reference the setup table. This does not change the verdict — the surrounding evidence and the to-do list's own "profile-bound" caveat (line 127) make the scope recoverable.
- The `4,096`-point `same_root_off_direct_off` row (`0.006583` sec, ratio `1.306x`) is the single largest relative slowdown in the matrix; the report correctly leads with the same-root-culling conclusion but could optionally call out that the relative cost of disabling culling shrinks with scale (`1.306x → 1.170x → 1.159x`), which is itself a useful signal about where culling matters most. Not required for this goal's diagnostic purpose.

## Conclusion

The artifact is internally consistent (every reported ratio and headline counter checks out against the raw JSON), the four-mode sweep is complete and repeated, and the interpretation — that dense candidate enumeration/root-read volume, not atomic-union traffic, is the dominant cost and the next thing to attack — is directly supported by the counters Goal3992 added and Goal3994 already validated as correctly wired. The report and its companion to-do-list update preserve the generic, app-agnostic native-engine vocabulary and carry the same conservative claim-boundary language (and `claim_boundary` JSON block) as the rest of this chain. Recommending `accept-with-boundary` — the same boundary the report itself states (diagnostic telemetry only; no release/performance/zero-copy/partner-selection/app-engine authorization), with the minor non-blocking suggestion to make the "exhausted" claim's profile/scale scope explicit in-line.
