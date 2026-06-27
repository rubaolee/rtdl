# Goal4183 Claude Review: Goal4182 Current 10-App Scale Packet

Date: 2026-06-09

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **accept-with-boundary**

---

## Scope

Read-only independent review of the Goal4182 current 10-app benchmark scale-profile packet
produced after the Goal4176-4181 RT-DBSCAN all-items direct-status work on an RTX 4000 Ada pod.

Files reviewed:

- `docs/reports/goal4182_current_benchmark_scale_profile_refresh_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4182_current_benchmark_scale_profile_refresh_rtx4000ada/current_scale_profile_packet.json`
- `tests/goal4182_current_benchmark_scale_profile_refresh_test.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `src/rtdsl/current_benchmark_route_decisions.py`

---

## Q1: Does the report accurately describe the packet and its boundaries?

**Yes.**

The report's claim counts, timing signals, and boundary text match the packet JSON at every
checked point:

- `all_pass: true`, `json_pass_count: 10` — confirmed in packet root.
- `working_tree_clean: true` — confirmed in `runtime_environment.working_tree_clean`.
- Source commit `79afb95a65bfb7a359efb56210294c89ec210060` — matches
  `runtime_environment.source_commit` exactly.
- GPU `NVIDIA RTX 4000 Ada Generation`, driver `550.127.08` — confirmed in
  `runtime_environment.nvidia_smi`.
- Timing signals in the report table are consistent with JSON:
  - RayJoin LSI speedup: report says `259.5x`; packet `lsi_scalar_count.rtdl_optix_speedup_vs_numba`
    = 259.478.
  - RayJoin overlay speedup: report says `212.9x`; packet `overlay_active_count.rtdl_optix_speedup_vs_numba`
    = 212.913.
  - RayJoin PIP one-shot: report says `0.252x`; packet `pip_one_shot.rtdl_optix_speedup_vs_numba`
    = 0.252.
  - RayJoin repeated PIP batch: report says `1.243x` per request; packet
    `pip_repeated_requests.per_request_speedup_vs_single_request` = 1.243.
  - RT-DBSCAN adapter: report says `0.096349s`; packet `elapsed_sec` = 0.09634859…
  - RT-DBSCAN grouped native: report says `0.090601s`; packet
    `grouped_native_sec` = 0.09060060…

The RayJoin workaround is honestly reported: public-CDB slice files were generated outside the
repository worktree using `scripts/goal2159_rayjoin_public_cdb_runner.py`, and the clean packet
ran from a clean worktree. The report and packet are consistent with each other.

---

## Q2: Does the artifact support only internal scale-profile/route-health evidence?

**Yes, at multiple enforced layers.**

**Packet root:** `release_authorized: false`, `public_speedup_claim_authorized: false`,
`broad_rt_core_claim_authorized: false`, `paper_reproduction_claim_authorized: false`.

**Per-row:** Every row's `semantic_stdout_check.claim_flag_violations` is `[]`.
The packet-level `validation.status` is `accept` with `errors: []`.

**Source enforcement:** `CurrentBenchmarkScaleProfile.__post_init__` in
`src/rtdsl/current_benchmark_scale_profiles.py` raises `ValueError` if any of the six
forbidden flags is set true. This means no scale-profile row can be registered with a
permissive claim flag — the prohibition is structural, not advisory.

Similarly, `CurrentBenchmarkRouteDecision.__post_init__` in
`src/rtdsl/current_benchmark_route_decisions.py` enforces nine forbidden flags on route
decisions, including `automatic_partner_selection_authorized`, `whole_app_speedup_claim_authorized`,
and `amd_performance_claim_authorized` — categories the packet does not attempt to authorize.

**Test coverage:** `test_packet_is_clean_all_pass_internal_evidence` calls `_flag_violations`
recursively over the full packet. `test_every_row_has_json_stdout_and_no_claim_leak` does the
same for each per-row stdout file. No claim-flag leak was observed in the files under review.

---

## Q3: Are all 10 benchmark app rows present, JSON-parseable, and claim-boundary clean?

**Yes.**

The packet `rows` array contains exactly 10 entries, one per promoted benchmark app:

| App | Row ID | Status | JSON-parseable | Claim violations |
|---|---|---|---|---|
| hausdorff_xhd | hausdorff_xhd_scale_default_optix_threshold | pass | true | [] |
| spatial_rayjoin | spatial_rayjoin_public_cdb_representative_mixed_route_scale_default | pass | true | [] |
| rt_dbscan | rt_dbscan_optix_numba_scale_default_65536_no_validation | pass | true | [] |
| robot_collision | robot_collision_optix_scale_default_1024_no_probe_reference | pass | true | [] |
| contact_manifold | contact_manifold_optix_scale_default_grid64 | pass | true | [] |
| raydb_style | raydb_style_optix_count_scale_default_262k | pass | true | [] |
| barnes_hut | barnes_hut_numba_scale_default_8192 | pass | true | [] |
| librts_spatial_index | librts_spatial_index_optix_scale_default_32768 | pass | true | [] |
| rtnn | rtnn_prepared_optix_scale_default_65536 | pass | true | [] |
| triangle_counting | triangle_counting_optix_rt_graph_2a1_scale_default_2048 | pass | true | [] |

All 10 per-row stdout JSON files exist in the local artifact directory
(`docs/reports/goal4182_current_benchmark_scale_profile_refresh_rtx4000ada/outputs/`).

The `summary.row_count` and `summary.app_count` are both 10. The `validation.status` is `accept`
with an empty error list.

---

## Q4: Is the RayJoin contract split described honestly?

**Yes.**

The `representative_hot_path_summary` in the spatial_rayjoin row reports:

| Contract | Recommended route | Evidence | Speedup |
|---|---|---|---|
| PIP one-shot | `numba_cuda_jit_scalar_count_no_rawkernel` | bounded slice favors simpler Numba code | 0.252x (OptiX is slower) |
| LSI scalar count | `rtdl_optix_prepared_segment_pair_count` | fused generic primitive avoids dense partner loop | 259.5x |
| Overlay active count | `rtdl_optix_prepared_shape_pair_active_count` | fused generic primitive avoids dense partner loop | 212.9x |
| Repeated PIP batch | `rtdl_optix_prepared_batch_executor` | prepared scene amortizes traversal setup | 1.243x per request |

The packet correctly describes PIP one-shot as Numba-favored with speedup < 1.0.
The LSI and overlay contracts are correctly described as RTDL/OptiX-favored with large speedups.
The repeated PIP batch benefit is modest and correctly described as a throughput (not latency)
pattern.

`automatic_dispatch: false` and `user_route_choice_visible: true` are present in
`recommended_route_summary`. The route decision in `current_benchmark_route_decisions.py` for
`spatial_rayjoin` uses `decision_kind="mixed_explicit"` and `partner_policy="mixed_explicit_user_choice"`,
consistent with the packet.

The test `test_rayjoin_contract_split_is_preserved` asserts all four contracts programmatically.
All assertions are consistent with the data.

---

## Q5: Missing tests, misleading wording, or next-step blockers?

**No blockers. Minor observations below.**

**Observation 1 — Barnes-Hut scale profile uses Numba (no-RawKernel), not CuPy.**
The route decision records `partner_policy="cupy_fastest_numba_reference"` because CuPy is the
fastest measured force continuation, while the scale profile uses `--partner numba` (no-RawKernel
reference path). This is not misleading: the profile's `purpose` string explicitly says "Goal4053
separately covers prepared grouped-vector stream reductions," and the payload's `rt_core_accelerated`
is `false` with explicit boundary text "Exact all-pairs force-vector reference path only." A
future scale packet could add a CuPy row alongside, but the current Numba row is the stated
intended profiling target.

**Observation 2 — RT-DBSCAN scale profile uses the conservative grouped-stream route.**
After the Goal4176-4177 all-items direct-status work, the declared direct-status route
(improving by 1.704x over grouped-stream at 2M road3d) remains an explicit unpromoted candidate.
The packet uses the grouped-stream route for the default 65k scale profile row. The Interpretation
section states this clearly: "the Goal4177 declared all-items route remains a separate explicit
proof route rather than a universal default." No misleading wording.

**Observation 3 — Test `test_report_states_non_authorizing_boundary` uses `text.replace("ten", "10")`.**
The report says "passed all ten promoted benchmark rows (`10/10`)" rather than writing `10/10`
twice. The test handles this with a string substitution. This is functional but slightly fragile.
Not a blocker; the test passes on the actual text.

**Observation 4 — Version string references Goal3828, not Goal4182.**
The packet version is `rtdl.v2_10.current_benchmark_scale_profiles.goal3828.v1` because Goal3828
defined the scale-profile registry schema. Goal4182 is the refresh run, not the schema revision.
This is the intended design and is not misleading.

**Observation 5 — No test for RayJoin input provenance.**
There is no test that the RayJoin CDB input files were generated via the public raw text path
rather than from committed CDB files. The packet records `data_dir` in the spatial_rayjoin
stdout, but the test suite does not verify the input path. This is a minor evidence gap: the
report's prose describes the materialization path honestly, but it is not machine-checked. Not
a blocker for using this packet as internal direction evidence.

---

## Verdict

**accept-with-boundary**

The packet is self-consistent, structurally enforced, claim-boundary clean across all 10 rows,
and honest about the RayJoin contract split and the RT-DBSCAN route position. The Barnes-Hut
and RT-DBSCAN observations above are consistent with the stated policy and do not introduce
misleading wording.

This packet is suitable as internal v2.10 direction evidence. It does not authorize a release,
public speedup claims, whole-app acceleration claims, or 3-AI consensus public claims. Any future
use for those purposes requires a separate user-requested artifact with external review.
