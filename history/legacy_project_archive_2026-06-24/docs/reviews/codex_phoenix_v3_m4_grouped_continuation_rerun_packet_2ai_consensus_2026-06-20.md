# Codex 2-AI Consensus: Phoenix V3 M4 Grouped-Continuation Rerun Packet

Date: 2026-06-20

Decision scope: whether the Phoenix V3 M4 grouped/fused-continuation rerun
packet is ready for RT hardware pod execution.

## Inputs

- Packet:
  `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.md`
- Machine-readable packet:
  `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json`
- External review:
  `docs/reviews/claude_phoenix_v3_m4_grouped_continuation_rerun_packet_review_2026-06-20.md`
- Source identity amendment review:
  `docs/reviews/claude_phoenix_v3_m4_no_git_source_identity_review_2026-06-20.md`
- Binding venv amendment review:
  `docs/reviews/claude_phoenix_v3_m4_binding_venv_review_2026-06-20.md`
- M10 event-accounting fix review:
  `docs/reviews/claude_phoenix_v3_m10_event_accounting_fix_review_2026-06-20.md`
- Final evidence classification review:
  `docs/reviews/claude_phoenix_v3_m4_final_evidence_review_2026-06-20.md`

## Consensus

Codex and Claude agree that the M4 rerun packet is the correct next Phoenix V3
P0 step after Goal4392 alignment and route-capability mapping.

Claude's verdict was `ACCEPT_WITH_REQUIRED_AMENDMENTS`. Codex applied the
required amendments:

- a pod-side pre-run claim-boundary gate reads the packet and verifies
  `release_authorized=false`, `public_speedup_claim_authorized=false`, and
  `phoenix_m7_qualified_release_rows=0`;
- the artifact directory is created, checked for write access, and free space
  is recorded before large M23/M28 outputs;
- failed serious-scale rows must be recorded at the stated scale and cannot be
  backfilled, averaged, or footnoted against old small-scale evidence;
- M9/M10/M11/M18/M23/M28 results cannot be used in public-facing or
  partner-facing material before a separate public-claim authorization;
- M28 requires independent labeled rows for `embree/count`, `embree/sum`,
  `optix/count`, and `optix/sum`.

After amendment, Codex consensus is:

```text
ACCEPT FOR POD EXECUTION.
NOT RELEASE EVIDENCE.
NOT PUBLIC SPEEDUP EVIDENCE.
NO V3 PUBLIC PERFORMANCE CLAIM AUTHORIZED.
```

## Source Identity Amendment

Pod preflight found that `/root/rtdl_v3_rebuild_20260620/current` is the
Phoenix current expanded worktree, with `VERSION=v3-rebuild-2026-06-20`, but it
does not contain a `.git` directory. Claude reviewed the no-git source-identity
fallback and accepted it with amendments.

Codex applied those amendments:

- git commit remains preferred when available;
- if no git worktree is present, the runner writes
  `current_commit.txt=no_git_worktree`;
- `source_identity_check.txt` records expected version
  `v3-rebuild-2026-06-20`, actual version, and `source_version_match=pass`;
- `provenance_search.txt` records where git and rebuild provenance were
  searched;
- `source_manifest.sha256` includes `build/librtdl_embree.so`,
  `build/librtdl_optix.so`, and `src/` plus `scripts/` source files;
- downstream reports must state that no-git source identity is VERSION-string
  plus file-hash based, not git-commit based.

## Binding Venv Amendment

Pod preflight also found that system `python3` lacks CuPy and Numba. The
existing rebuild venv at `/root/rtdl_v3_rebuild_20260620/.venv/bin/python`
passed the GPU partner gate with `cupy-cuda12x==14.1.1`, `numba==0.65.1`, and
`torch==2.6.0+cu124`.

Claude reviewed the amendment and accepted it with required safeguards. Codex
applied those safeguards:

- the packet records the exact binding interpreter and package versions;
- the pod run must reverify GPU partner, source identity, and claim-boundary
  gates with that interpreter;
- system `python3` failure is recorded as a missing-CuPy/Numba packaging gap,
  not as V3 M4 code-path failure;
- focused tests and measurement commands use the binding venv, and inspected
  Python re-exec/subprocess paths use `sys.executable`.

## Final Evidence Consensus

Codex and Claude agree that the Phoenix M4 pod execution can be accepted as
internal M4 evidence, with these controlling boundaries:

```text
release_authorized=false
public_speedup_claim_authorized=false
Phoenix M7-qualified release rows=0
```

Evidence report:

```text
docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md
```

Machine-readable evidence index:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json
```

Final classification:

- M9: pass_internal.
- M10: pass_internal_with_accounting_warning, not a clean pass.
- M11: pass_internal_measured_window.
- M18: pass_internal.
- M23: pass_internal.
- M28: pass_internal_same_contract_cpu_reference_only.

Remaining blockers before any release/public claim:

- M10 accounting warning must remain visible in rollups.
- System `python3` missing CuPy/Numba remains an open packaging gap before M7.
- M28 internal ratios must not be cited as cross-backend speedup until M7
  qualification.
- No row from this M4 run is public-release evidence.

## Validation

Local validation after amendments:

```text
py -3 -m unittest tests.v3_phoenix_m4_grouped_continuation_packet_test tests.v3_release_wording_gate_test
Result: 6 tests OK.

py -3 scripts/v3_release_wording_gate.py --pretty
Result: pass.

py -3 scripts/run_test_matrix.py --group v3_rebuild
Result: 11 modules, 39 tests OK.
```

## Goal-Level Decision Audit

Decision: run the Phoenix V3 M4 grouped/fused-continuation packet on the RT
hardware pod.

1. Was I foolish?

   No, after amendment. The decision is bounded, evidence-first, and tied to
   Goal4392 M4 instead of broad release language.

2. If yes, what actions made the decision foolish?

   The pre-amendment version was procedurally weak because some safeguards were
   policy statements rather than runner-visible gates. That weakness is now
   fixed by packet-read gates, artifact preflight, failure recording rules, and
   independent M28 row requirements.

3. Was there another path?

   Yes. Phoenix could start with Barnes-Hut regression repair or RayJoin
   topology analysis. M4 is chosen first because reusable grouped/fused
   continuation is the core V3 language capability that can connect DBSCAN and
   non-DBSCAN workloads.

4. Can I now try a different path that actually solves the problem?

   Yes. The immediate path is pod execution of this M4 packet. If M4 fails, the
   next path is to record the failed rows and repair the generic continuation
   machinery directly, not to replace the evidence with smaller old rows.
