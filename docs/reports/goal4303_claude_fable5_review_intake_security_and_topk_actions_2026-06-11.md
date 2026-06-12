# Goal4303: Claude Fable5 Review Intake, Security Guard, and Numba Top-K Action

Date: 2026-06-11

## Source Review

This report intakes the fresh Claude Fable5 whole-project review:

`docs/reviews/goal4302_claude-fable5_whole_project_critical_review_and_improvement_suggestions_2026-06-11.md`

Claude's verdict was `accept-with-boundary`. The review identified four
highest-priority project risks:

1. Operational security leakage from private-key-shaped files and tracked pod
   connection strings.
2. The mismatch between the teaching kernel DSL and the high-performance
   prepared primitive/catalog path.
3. The monolithic, hand-written partner adapter layer.
4. Process/report/test ceremony weight that now slows product work.

This goal does not claim to close the whole review. It takes the first concrete
actions that are safe and high-leverage immediately.

## Actions Completed

### F1 Security Hygiene

- Moved the untracked root-level private-key-shaped file out of the repository
  root into a local archive outside the repository. The exact filename and
  destination are intentionally not repeated in this tracked report.

- Moved the untracked root-level debris named in the Fable5 review out of the
  repository root into the same local archive area outside the repository:
  `before_3958.txt`, `rtdl_v0_4.tar.gz`, and `Lib/`.

- Hardened `.gitignore` with local secret/debris patterns:
  - `id_ed25519*`
  - `*.pem`
  - `*.ppk`
  - `*.key`
  - `/Lib/`
  - `/before_*.txt`
  - `/rtdl_v0_4.tar.gz`

- Redacted live pod SSH endpoints and local key names from current tracked
  goal42xx/goal43xx evidence files:
  - `docs/reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md`
  - `docs/reports/goal4218_mixed_route_focus_after_policy_2026-06-09.md`
  - `docs/reports/goal4222_rtdbscan_blocked_vs_unblocked_profile_map_2026-06-09.md`
  - `docs/reports/goal4223_rayjoin_public_cdb_contract_scale_map_2026-06-09.md`
  - `docs/reports/goal4225_release_prep_current_scale_packet_2026-06-09.md`
  - `docs/reports/goal4297_remote_pod_driver_explicit_toolchain_env_2026-06-11.md`

- Redacted the copied Fable5 review file itself so the tracked review no
  longer repeats the private-key header, local key filename, or live root SSH
  command that it originally cited.

- Added `tests/goal4303_current_security_redaction_guard_test.py`.

The new guard checks that current reports/handoffs/reviews do not contain
private-key headers, live root SSH command strings, the old working-key
filename, local Windows identity-file examples, or raw IPv4 endpoint strings.
It deliberately targets the current goal42xx/goal43xx surface; the broader
historical archive still needs a planned redaction/archive pass.

### P3 Numba Grouped Top-K

Claude's prioritized improvement plan listed generic Numba `grouped_topk_f64`
as P3. Goal4301 implemented that action:

- Added generic Numba `grouped_topk_f64` descriptor/operation/runner.
- Added a device kernel for equal contiguous grouped score segments.
- Added Numba support to `grouped_topk_f64_partner_columns`.
- Rewired `top_k_nearest_points_2d_partner_columns(..., partner="numba")` so
  current RTNN/ANN top-k no longer materializes score rows on the host for
  ranking.

See:

`docs/reports/goal4301_numba_grouped_topk_device_rank_2026-06-11.md`

The scaled local Linux artifact records:

```json
{
  "query_count": 384,
  "candidate_count": 384,
  "numba_score_row_count": 147456,
  "v2_11_numba_preview_kernel_status": "device_grouped_topk_after_device_score_rows",
  "host_rank_materialization_used": false
}
```

## Validation

Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4303_current_security_redaction_guard_test
Ran 2 tests
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4299_numba_topk_partner_reference_test tests.goal4298_v2_11_embree_cpu_partner_reference_packet_test
Ran 14 tests
OK (skipped=3)

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4303_current_security_redaction_guard_test tests.goal4299_numba_topk_partner_reference_test tests.goal4298_v2_11_embree_cpu_partner_reference_packet_test
Ran 17 tests
OK (skipped=3)

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4308_rtnn_embree_front_door_test tests.goal4298_v2_11_embree_cpu_partner_reference_packet_test tests.goal4307_editable_source_tree_onboarding_test tests.goal4306_partner_column_contracts_foundation_test tests.goal4305_fable5_evidence_and_process_docs_test tests.goal4303_current_security_redaction_guard_test tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4299_numba_topk_partner_reference_test
Ran 31 tests
OK (skipped=4)

Current-goal redaction scan:

Scanned 196 current goal42xx/goal43xx report, handoff, and review files; zero
private-key, live-root-SSH, old working-key-name, Windows identity-file, or raw
IPv4 endpoint-string violations were found.
```

Local Linux fresh validation checkout:

`/home/lestat/work/rtdl_goal4301_check`, base commit `bf12a82b`, with only this
goal's touched files copied in.

```text
PYTHONPATH=src:. python3 -m unittest tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4303_current_security_redaction_guard_test tests.goal4299_numba_topk_partner_reference_test
Ran 11 tests
OK
```

The Linux run executed the Numba CUDA checks; the warnings were only Numba
low-occupancy warnings from tiny correctness fixtures.

## Still Open From Claude Fable5

These are not closed by Goal4303:

- F2/P4: Decide whether the public language story is "kernel DSL lowers to
  performance routes" or "primitive catalog and composition first".
- F3/P2: Split `partner_adapters.py` fully. Goal4306 added the first shared
  partner-column contract layer, but the monolith split remains open.
- F4/P9/P12: Reduce process/report/test ceremony and archive old evidence.
- F6/P5: Apply the 1-second aggregate timing floor to the main ten-app packet.
- F8/P10: Deduplicate repeated claim-boundary prose.

Follow-up goals narrowed several of these items:

- Goal4305 added the conservative RT-core evidence matrix and goal-tier
  protocol.
- Goal4306 added the first explicit partner-column contract layer.
- Goal4307 added optional editable source-tree onboarding without making a
  package-install support claim.
- Goal4308 removed the v2.11 RTNN Embree packet exception by adding a bounded
  Embree ANN candidate-quality front door.

## Boundary

Goal4303 does not authorize release action, public speedup wording,
package-install claims, true-zero-copy claims, broad RT-core claims, automatic
partner selection, or paper-reproduction wording.
