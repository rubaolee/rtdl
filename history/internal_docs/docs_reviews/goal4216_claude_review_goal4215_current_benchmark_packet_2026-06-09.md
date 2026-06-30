# Goal4216: Claude Review of Goal4215 Current Benchmark Packet After RT-DBSCAN Policy Cleanup

Date: 2026-06-09

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **accept-with-boundary**

---

## Scope

This review covers:

- `docs/reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md`
- `docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/current_scale_profile_packet.json`
- `docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/rayjoin_fixture_materialization.json`
- `tests/goal4215_current_benchmark_scale_profile_after_policy_test.py`

Context reviewed: Goal4205-4212 RT-DBSCAN boundary policy reports, independently
confirming the canonicalization chain that preceded this packet.

---

## Q1: Do all ten current benchmark front doors genuinely pass on RTX 4000 Ada at commit 63289bbc?

**Finding: Yes.**

The packet carries `"all_pass": true`, `"json_pass_count": 10`, and
`"summary.row_count": 10`. Runtime environment confirms:

- `source_commit_short: "63289bbc"` matches the stated source commit
  (`63289bbcd74326e0b44b865a3f66061cb49e823d`).
- `nvidia_smi: "NVIDIA RTX 4000 Ada Generation, 550.127.08, 20475 MiB"` confirms
  the target hardware and driver.
- All ten rows carry `"returncode": 0`, `"status": "pass"`, and
  `"stdout_json_parseable": true`.
- All ten rows carry `"claim_flag_violations": []`.
- All ten apps are distinct in the `"app"` field; no row is duplicated.
- All ten rows have non-zero `stdout_bytes` and reference file-backed stdout
  paths that are present locally and parseable.

**Engineering note on `working_tree_clean: false`.**
The packet's `git_status_short` field shows only
`"?? docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/"`.
This is the artifact output directory created by the runner before recording the
snapshot metadata. No source files were modified on the pod. The explanation in
the report is accurate and adequate.

**Engineering note on Barnes-Hut `rt_core_accelerated: false`.**
The Barnes-Hut row uses the partner-exact-force path (`--partner numba`), which
is the reference path without RT-core acceleration. `rt_core_accelerated: false`
in the payload is correct for this row. The packet correctly classifies it in
`numba_required_rows` rather than as an RT-core claim.

---

## Q2: Is the RayJoin fixture repair correctly classified as environment/data-materialization?

**Finding: Yes.**

The `rayjoin_fixture_materialization.json` records only file metadata: `path`,
`bytes`, `chains`, `count`, `segments`, `source`, `start`. No timing data or
performance result is captured in this artifact. The repair was a missing
fixture directory on the pod (`.cdb` files absent), not a code change. The
materialization script (`goal2159_rayjoin_public_cdb_runner.py`) produced the
two needed slices through its standard dry-run materialization path.

The fixture JSON carries an explicit `claim_boundary` object with:

- `"v2_0_release_authorized": false`
- `"whole_app_rayjoin_speedup_claim_authorized": false`
- `"broad_rt_core_speedup_claim_authorized": false`
- `"paper_scale_perf_claim_authorized": false`

The final RayJoin benchmark row then passes with `all_contract_counts_match: true`
and `contract_count: 4`. The hot-path speedup values (LSI `262.5x`, overlay
`212.2x`) are route-specific contract medians, not whole-app claims, and carry
`"public_speedup_claim_authorized": false`.

**Note:** The CPU backend in the fixture materialization records `"status":
"dry_run"`, which is appropriate for the LSI-case materialization path used here.

---

## Q3: Does the packet verify RT-DBSCAN canonical `single_pass_candidate_root_rebased` policy?

**Finding: Yes — independently verified from the output JSON.**

The following fields were confirmed directly in
`outputs/rt_dbscan_optix_numba_scale_default_65536_no_validation.stdout.json`:

| Field | Value |
|---|---|
| `metadata.boundary_assignment_policy` | `"single_pass_candidate_root_rebased"` |
| `metadata.boundary_assignment_canonical_policy` | `"single_pass_candidate_root_rebased"` |
| `metadata.grouped_stream_continuation_pass_count` | `1` |
| `metadata.native_grouped_stream_metadata.boundary_assignment_policy` | `"single_pass_candidate_root_rebased"` |
| `metadata.native_grouped_stream_metadata.boundary_assignment_pass_count` | `1` |

These match what the Goal4211/4212 reports established. The test
`test_rtdbscan_uses_canonical_single_pass_policy_in_broad_packet` in
`tests/goal4215_current_benchmark_scale_profile_after_policy_test.py` asserts
all five of these fields and would fail if any differed.

The RT-DBSCAN row uses `--no-validation`, which is correct for a scale-profile
run. The repeat protocol shows `signatures_stable: true` across measured runs,
confirming output stability without re-running the full validation path.

---

## Q4: Are all release/public-claim boundaries closed?

**Finding: Yes.**

A grep scan over all files in
`docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/`
found zero instances of any forbidden flag set to `true`. The only `_authorized:
true` instances present are:

- `direct_device_handoff_authorized: true` — internal device memory handoff
  protocol descriptor; not a public claim flag.
- `output_columns_true_zero_copy_authorized: true` — internal native output
  column reuse descriptor; distinct from the forbidden
  `true_zero_copy_authorized` / `true_zero_copy_claim_authorized` keys, both of
  which appear as `false` throughout the RT-DBSCAN output.
- `generic_ray_triangle_rt_core_subpath_authorized: true` — internal protocol
  descriptor in the triangle counting output; not a public release flag.

None of these appear in the `FORBIDDEN_TRUE_FLAGS` set defined in the test file.

At the packet level:
- `"release_authorized": false`
- `"public_speedup_claim_authorized": false`
- `"broad_rt_core_claim_authorized": false`
- `"paper_reproduction_claim_authorized": false`

are all confirmed false. The `summary.status` is
`"internal_scale_profile_registry_not_release_authorization"`, which is the
correct non-release status.

No row has a non-empty `claim_flag_violations` list.

---

## Q5: Does the report avoid overclaiming the packet?

**Finding: Yes.**

The report explicitly states:

> "This is an engineering health packet. It does not authorize release action,
> public speedup wording, whole-app acceleration wording, broad RT-core wording,
> paper-reproduction wording, true-zero-copy wording, automatic partner
> selection, AMD performance wording, or app-specific native-engine logic."

And in the Interpretation section:

> "The packet is not a final performance release table. It is a current-route
> health and direction packet. It deliberately keeps release/public claim flags
> false."

The three listed interpretations (front door health after policy cleanup;
canonical policy confirmation in the broad packet; mixed-route story honesty) are
all adequately scoped. The report does not use language that could be read as
authorizing any public claim.

---

## Summary of Findings

| Question | Finding |
|---|---|
| All ten rows pass at 63289bbc on RTX 4000 Ada | Confirmed |
| RayJoin repair correctly classified as environment/data | Confirmed |
| RT-DBSCAN canonical policy verified in broad packet | Confirmed (independently from output JSON) |
| All release/public-claim boundaries closed | Confirmed (zero forbidden flags set true) |
| Report avoids overclaiming | Confirmed |

---

## Verdict: accept-with-boundary

The packet provides sufficient internal engineering evidence to accept as a
post-policy-cleanup health packet. The five review questions are answered
affirmatively. The RT-DBSCAN canonical policy is verified both by the test
assertions and by direct inspection of the output JSON.

**Boundary statement — this review does not authorize:**

- Release action of any kind
- Public speedup wording
- Whole-app acceleration wording
- Broad RT-core acceleration wording
- Paper-reproduction wording
- True-zero-copy wording
- Automatic partner selection
- AMD performance wording
- App-specific native-engine logic

Any future release packet requires separate user authorization and the required
multi-AI consensus process. This review is internal engineering evidence only.
