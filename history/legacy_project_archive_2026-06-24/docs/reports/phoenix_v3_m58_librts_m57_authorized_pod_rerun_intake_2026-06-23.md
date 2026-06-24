# Phoenix V3 M58 LibRTS M57-Authorized POD Rerun Intake

Date: 2026-06-23

Status:

```text
m58_evidence_copied_back_yellow_watch_rows_open_pending_external_review
```

## Scope

M58 executed exactly one M57-authorized, source-signature-gated LibRTS M47 POD
rerun.

Authorization source:

- `docs/reviews/codex_claude_antigravity_phoenix_v3_m57_one_rerun_authorization_3ai_consensus_2026-06-23.md`

Authorized token used exactly once:

```text
M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED
```

Run script:

```text
scripts/v3_phoenix_m47_librts_stability_protocol.py
```

## POD Environment

- Host: `2bcb58b259e4`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- Current root: `/root/rtdl_v3_rebuild_20260620/current`
- V2.14 root: `/root/rtdl_v3_rebuild_20260620/v2_14`
- Current Python: `/usr/bin/python3`
- V2.14 Python: `/usr/bin/python3`

Current-tree sync before run:

- remote backup:
  `/root/rtdl_v3_rebuild_20260620/m58_backup_20260624_0049/current_m57_files_before_sync.tgz`
- synchronized files:
  - `scripts/v3_phoenix_m47_librts_stability_protocol.py`
  - `src/rtdsl/prepared_execution.py`
  - `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
  - `tests/v3_phoenix_librts_aabb_count_runner_test.py`
  - `tests/v3_phoenix_prepared_execution_session_runner_test.py`
  - `tests/v3_phoenix_aabb_prepared_query_cache_test.py`

## Copy-Back Evidence

Target-machine dry-run/preflight-only evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_target_dry_run_20260624_0054/`
- tarball:
  `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_target_dry_run_20260624_0054.tgz`
- sha256:
  `2f1c1218cd4f344521cd2e32d8ccf7eec3ef12e5f50bd7df1ff4e99637d7b4f7`

Execution evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055/`
- tarball:
  `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055.tgz`
- sha256:
  `e026cc740cb3ddc51931f4fd7fd509a59568525442409f82849169112d655794`

Execution copy-back contents:

- measured stdout JSON files: `32`
- stderr/preflight text files: `39`
- required `summary.json`: present
- required driver log: `m58_execution_driver.log`

## Dry-Run / Source-Signature Gate

Target dry-run was executed with:

```text
--run-preflight
```

Dry-run status:

```text
m47_librts_stability_protocol_preflight_only_no_pod_not_release
```

Dry-run checks:

- `failed_checks=[]`
- `current_librts_set_b_source_signature.returncode=0`
- `preflight_current_librts_set_b_source_signature.stdout.txt` contains
  `"failed": []`
- all eight source-signature markers are true

## Execution Summary

Execution status:

```text
m47_librts_stability_protocol_run_complete_not_release
```

Top-level checks:

- `failed_checks=[]`
- `run_errors={}`
- scenarios: `2`
- sample count per scenario: `8`
- schedule rows: `32`
- all claim-boundary booleans: false

## Scenario Intake

| Scenario | M47 label | Geomean | Median | Min | Max | Pass count >=0.95 | First-sample-stripped geomean | Metadata failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `embree_32768_stress` | `yellow_stability_boundary_watch_row_open` | 1.030501x | 1.022440x | 0.870986x | 1.225962x | 6/8 | 1.055558x | none |
| `optix_cold_single_shot` | `yellow_stability_boundary_watch_row_open` | 0.979485x | 0.938318x | 0.833096x | 1.210241x | 3/8 | 1.002400x | none |

Important read:

- The M55 metadata failure `set_b_control_candidate_missing` is cleared in the
  sampled M58 paired rows.
- Both rows remain `yellow_stability_boundary_watch_row_open`, not green.
- Do not call either watch row closed from this intake.

## Interpretation Boundary

This intake does not authorize or claim:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure

The correct next step is external review of this copied evidence. Any
watch-row closure, public wording, or follow-on run requires a separate review.

## Goal-Level Decision Audit

Decision: record M58 as a copied evidence intake with both LibRTS watch rows
yellow/open, and request external review before interpretation.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   calling yellow/open evidence success or rerunning again after the single M57
   token was consumed.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Preserve the evidence, report the labels exactly, and request external
   review before any claim.
4. Can I now try a different path that actually solves the problem? Yes. Submit
   the copied M58 evidence for review and only then decide whether LibRTS needs
   more runtime work or can remain a yellow/open stability row.
