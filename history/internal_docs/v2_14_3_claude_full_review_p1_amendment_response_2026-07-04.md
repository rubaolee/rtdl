# v2.14.3 Claude Full Review P1 Amendment Response

Date: 2026-07-04

Source review:

```text
history/internal_docs/claude_review_v2_14_3_full_technical_release_2026-07-04.md
```

Review verdict:

```text
approve_technical_packet_but_require_release_staging_cleanup
```

## Summary

Claude approved the v2.14.3 technical packet but required staging cleanup before human push.

This response records the handling of each P1 item.

## P1-1: Bound The "Core Genericity" Claim

Status:

```text
amended
```

Action:

- Updated `history/internal_docs/v2_14_3_technical_report_architecture_generic_design_performance_2026-07-04.md`.
- Updated `history/internal_docs/goal4987_v2_14_3_closeout_cleanup_release_packet_2026-07-04.md`.

New wording:

```text
The new v2.14.3 primitives and public route are generic.
Legacy rayjoin_cdb native symbols and bundled rtdsl.rayjoin_overlay remain in-tree pending rename/relocation.
```

This avoids the false absolute claim that RTDL core has no remaining RayJoin identity traces.

## P1-2: Non-RayJoin Runtime Genericity Evidence

Status:

```text
closed with local Linux runtime smoke
```

Attempted POD command:

```text
ssh -o BatchMode=yes -o ConnectTimeout=10 -p 10626 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod root@213.173.108.6 "... python -m unittest tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test"
```

Result:

```text
banner exchange: Connection to UNKNOWN port -1: Connection refused
```

Current release-stage boundary:

```text
The POD was unavailable, but the non-RayJoin GPU runtime genericity subtest was rerun on local Linux.
```

Local Linux runtime check:

```text
host: lx1 / 192.168.1.20
GPU: NVIDIA GeForce GTX 1070
driver: 580.126.09
```

Method:

```text
Copied current v2.14.3 src/rtdsl and tests/goal4948_non_rayjoin_hit_stream_numba_genericity_test.py
to /home/lestat/work/v2143_p1_runtime_check.

Used existing local Linux native library:
/home/lestat/work/v2_v3_v4_serious_lx1_20260619_221102/build/librtdl_optix.so
```

Command:

```text
cd /home/lestat/work/v2143_p1_runtime_check
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/home/lestat/work/v2_v3_v4_serious_lx1_20260619_221102/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/home/lestat/work/v2_v3_v4_serious_lx1_20260619_221102/build/librtdl_optix.so
python3 -m unittest tests.goal4948_non_rayjoin_hit_stream_numba_genericity_test
```

Result:

```text
Ran 2 tests in 0.714s
OK
```

Interpretation:

This closes the skipped local Windows runtime gap for release staging. It is a functional genericity smoke, not a performance measurement.

## P1-3: Performance Matrix Provenance

Status:

```text
amended
```

Action:

- Updated `history/internal_docs/goal4985_v2_14_3_final_performance_matrix_2026-07-04.md`.

New boundary:

```text
7.851s -> 4.220s is a bounded evidence-chain comparison.
It is not a same-session benchmark suite result.
```

If a publication-grade performance table is required, the normal route, exact-LSI route, fast-pack route, and repeated full route must be rerun in one POD session.

## P1-4: Internal Docs Staging Risk

Status:

```text
amended as staging gate
```

Action:

- Updated `history/internal_docs/goal4987_v2_14_3_closeout_cleanup_release_packet_2026-07-04.md`.

New rule:

```text
history/internal_docs/ must be explicitly excluded from public artifacts unless intentionally archived as internal history.
```

Rationale:

The internal docs intentionally contain goal IDs, reviewer names, process language, and review artifacts. They are valuable internal evidence, but they must not be accidentally exposed as user-facing release material.

## Current Status After Amendments

Resolved for staging documentation/runtime gate:

- P1-1
- P1-2
- P1-3
- P1-4

Final release staging can state that non-RayJoin hit-stream row-buffer genericity has a local Linux GPU runtime smoke. It must still avoid performance claims from this smoke.
