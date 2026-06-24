# Phoenix V3 M4 Grouped-Continuation Pod Evidence

Status: internal Phoenix M4 evidence, not release evidence, 2026-06-20.

This report records the first Phoenix P0 pod execution for Goal4392 M4:
generic fused/grouped continuation with cross-app reuse. It does not authorize
V3 release wording, public speedup wording, whole-app speedup wording, automatic
partner/backend selection, or public zero-copy wording.
In short: this report does not authorize public speedup wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

Artifact directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620
```

Machine-readable evidence index:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json
```

## Pod Gates

The run used the Phoenix current expanded worktree:

```text
/root/rtdl_v3_rebuild_20260620/current
VERSION=v3-rebuild-2026-06-20
current_commit.txt=no_git_worktree
```

Because the pod tree is not a git checkout, source identity is
VERSION-string plus file-hash based, not git-commit based. The run preserves
`source_identity_check.txt`, `provenance_search.txt`, and
`source_manifest.sha256`.

The binding Python environment was:

```text
/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

System `python3` failed the GPU partner gate because CuPy and Numba were
missing. The binding venv passed the GPU partner gate. This is recorded in:

- `system_python3_gpu_env_gate.json`: `status=fail`
- `gpu_env_gate.json`: `status=pass`

Open packaging gap:

- ID: `phoenix_m4_system_python_missing_cupy_numba`
- Owner: Phoenix V3 rebuild owner
- Target fix milestone: before Phoenix M7 release qualification
- Status: open
- Meaning: M4 evidence is bound to the rebuild venv until standard packaging is
  repaired.

Pre-run claim-boundary and artifact-space gates passed. Artifact free space was
20,812,021,760 bytes before the large runs.

Focused capability tests passed after synchronizing the internal report
fixtures required by the tests:

```text
Ran 41 tests in 0.316s
OK
```

## Results

| Gate | Scale | Result |
| --- | ---: | --- |
| M9 grouped stream partner | 65,536 points | pass; CuPy and Numba signatures match |
| M10 same-stream evidence | 65,536 points | non-clean pass; accounting warning count = 1; `true_zero_copy_ready=false` |
| M11 measured-window no-hidden-copy | 65,536 points | pass; transfer counter observed |
| M18 device-side grouped contract | 65,536 rays / 1,024 groups | pass |
| M23 DBSCAN component bridge | 65,536 copies / 524,288 points | pass |
| M28 RayDB grouped reduction | 262,144 rows / 1,024 groups | pass; four independent backend/mode rows |

### M9

Artifact: `m9_grouped_stream_partner_65536.json`

- Status: `m9_device_resident_partner_rows_no_public_claim`
- Point count: 65,536
- Signature match: true
- CuPy median: 1.102805 ms
- Numba median: 0.834696 ms
- Winner inside this internal row: Numba
- Public claim authorized: false

### M10

Artifact: `m10_same_stream_65536.json`

- Status: `m10_same_stream_event_evidence_internal_claims_gated`
- Point count: 65,536
- Same-stream ready: true
- Signature match: true
- `true_zero_copy_ready`: false
- CuPy total event median: 0.787840 ms
- Numba total event median: 0.791296 ms
- Event-accounting status:
  `succeeded_with_independent_median_accounting_warning`
- Event-accounting warning count: 1

The warning is important. Native-event, partner-event, and total-event medians
are computed independently across repeats. The strict gate is per-sample event
validity; the independent median sum is an accounting approximation. This M10
row is therefore not a clean pass. It is a pass with accounting warning.

### M11

Artifact: `m11_no_hidden_copy_65536.json`

- Status: `m11_transfer_counter_no_hidden_column_copy_internal_claims_gated`
- Point count: 65,536
- Same-stream ready: true
- Transfer counter observed: true
- No hidden column copy ready: true
- Internal `true_zero_copy_ready`: true

This is an internal measured-window result. It does not authorize public
zero-copy wording or product-wide zero-copy claims.

### M18

Artifact: `m18_device_grouped_65536.json`

- Status: `m18_device_side_grouped_argmin_contract_internal_claims_gated`
- Ray count: 65,536
- Group count: 1,024
- Partners: CuPy and Numba
- Signature match: true
- Prepare, hot window, and measured window no-hidden-column-copy readiness:
  true
- Public claim authorized: false

### M23

Artifact: `m23_dbscan_component_signature_524288.json`

- Status:
  `m49_dbscan_app_uses_compact_component_signature_without_python_row_materialization`
- Copies: 65,536
- Point count: 524,288
- Output mode: `component_signature`
- Partner count: 2
- Native continuation active: true
- RT-core accelerated: true
- Oracle/signature checks: true
- Public claim authorized: false

### M28

Artifact: `m28_raydb_grouped_reduction_262144.json`

- Status: `ok`
- Generated rows: 262,144
- Generated groups: 1,024
- CPU reference match: true
- Public speedup claim authorized: false

Independent evidence rows:

| Backend | Mode | Median seconds | Matches CPU reference |
| --- | --- | ---: | --- |
| Embree | count | 0.009120 | true |
| Embree | sum | 0.999516 | true |
| OptiX | count | 0.000925 | true |
| OptiX | sum | 0.004929 | true |

Internal same-contract ratios:

- Count: Embree/OptiX median = 9.864x
- Sum: Embree/OptiX median = 202.774x

These ratios are internal same-contract route evidence only. They do not
authorize public speedup wording. They are internal CPU-reference comparisons
only and must not be cited as cross-backend speedup until M7 qualification.

## Evidence Index Flags

The machine-readable index attaches the same pod source identity and claim
boundary to each result row:

- source identity: `no_git_worktree / v3-rebuild-2026-06-20`
- source manifest: `source_manifest.sha256`
- `release_authorized=false`
- `public_speedup_claim_authorized=false`
- `public_claim_authorized=false`
- `public_zero_copy_wording_authorized=false`
- `phoenix_m7_qualified=false`

M10 is explicitly classified as
`pass_internal_with_accounting_warning`, with `clean_pass=false` and
`accounting_warning_count=1`.

## Interpretation

Phoenix M4 now has serious-scale pod evidence that the current V3 tree can run
generic grouped/fused continuation routes across:

- partner-backed component union: M9, M10, M11, M23;
- device-side grouped contracts: M18;
- non-DBSCAN grouped reduction: M28.

The strongest positive result is that DBSCAN and RayDB both instantiate named
generic V3 continuation capabilities at non-toy scale. The main caveat is M10:
same-stream evidence passes, but one partner row carries an independent-median
accounting warning and must remain visibly qualified.

This evidence moves Phoenix M4 forward. It does not complete M7, does not make
V3 broadly faster than V2.14, and does not make any current public release
claim safe.

## Goal-Level Decision Audit

Decision: accept this pod run as internal Phoenix M4 evidence and proceed to
classification/repair planning from the artifacts.

1. Was I foolish?

   No, not after correcting the environment, provenance, fixture, and M10
   accounting issues. The run preserved failures and warnings instead of hiding
   them.

2. If yes, what actions would have made the decision foolish?

   It would have been foolish to call the first M10 failure a pass, to downshift
   the scale, to hide the accounting warning, or to present M28 internal ratios
   as public speedup claims.

3. Was there another path?

   Yes. We could have stopped at the first M10 failure and marked M4 blocked.
   The better path was to inspect the failure, fix the invalid median-sum
   assertion with external review, and rerun the same serious scale.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is to classify these M4 rows, decide whether M10's
   accounting warning requires deeper instrumentation repair, and then continue
   Phoenix with the next Goal4392 gate rather than claiming release success.
