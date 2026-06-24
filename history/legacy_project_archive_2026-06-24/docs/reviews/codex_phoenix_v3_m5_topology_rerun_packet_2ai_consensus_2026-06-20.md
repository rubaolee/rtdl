# Codex 2-AI Consensus: Phoenix V3 M5 Topology Rerun Packet

Date: 2026-06-20

Scope: approve the Phoenix V3 M5 topology packet for pod execution as internal
V3-only evidence, not release evidence.

## External Review

Claude review:

`docs/reviews/claude_phoenix_v3_m5_topology_rerun_packet_review_2026-06-20.md`

Verdict: approve with amendments.

Claude's required amendments:

1. prove the wording gate explicitly covers the M5 packet files;
2. add fail-closed OptiX/RT hardware gating, not only `nvidia-smi` logging;
3. equalize or justify repeat counts;
4. make generated artifacts headline `query_exec` missing as M5 author-code
   blocked.

## Amendments Applied

- `scripts/v3_release_wording_gate.py` now supports `--require-scanned`.
- `tests/v3_release_wording_gate_test.py` now asserts the M5 `.md` and `.json`
  packet files are scanned and can be required explicitly.
- `scripts/v3_optix_hardware_gate.py` was added as a fail-closed
  NVIDIA OptiX/RT hardware precondition gate.
- `tests/v3_optix_hardware_gate_test.py` covers RTX pass, non-RT GPU fail, and
  empty `nvidia-smi` fail-closed behavior.
- `scripts/v3_phoenix_m5_topology_intake.py` was added to validate pod
  artifacts and top-line the M5 author-code comparison status.
- `tests/v3_phoenix_m5_topology_intake_test.py` verifies missing `query_exec`
  becomes `partial_internal_evidence_author_code_blocked`, not release success.
- `docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.md` and
  `.json` now include the hardware gate, equal 1000 OptiX/Embree repeats, and
  intake summary generation.

## Verification

Explicit wording-gate coverage:

```text
py -3 scripts\v3_release_wording_gate.py --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.md --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.json --pretty
status: pass
missing_required_scanned_files: []
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

Affected tests:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_optix_hardware_gate_test tests.v3_phoenix_m5_topology_packet_test tests.v3_phoenix_m5_topology_intake_test
10 tests OK
```

Full Phoenix V3 rebuild matrix:

```text
py -3 scripts\run_test_matrix.py --group v3_rebuild
15 modules, 53 tests OK
```

## Consensus

Codex agrees with Claude that the original packet was acceptable only after the
four amendments. Those amendments are now applied and locally verified.

Decision: proceed to pod execution for M5 internal topology evidence.

Boundaries:

- release authorization remains false;
- public speedup wording remains false;
- Phoenix M7-qualified release rows remain 0;
- if `query_exec` is missing, M5 author-code comparison is blocked;
- RTDL-only same-contract topology rows are internal evidence, not RayJoin paper
  reproduction.

## Goal-Level Decision Audit

Decision: execute the amended M5 topology packet on the pod.

1. Was I foolish?

   No. The decision now follows external review, applies all P0/P1 amendments,
   and has local gates proving the packet is fenced.

2. If yes, what actions would make it foolish?

   It would be foolish to skip the new hardware gate, ignore missing
   `query_exec`, or interpret M5 internal ratios as public V3 release claims.

3. Was there another path?

   Yes. We could reject M5 until author `query_exec` is found. The chosen path
   is better because it still collects RTDL same-contract topology evidence
   while making author-code completion blocked at the top level.

4. Can I now try a different path that actually solves the problem?

   Yes. The amended packet either produces validated internal M5 evidence or
   fails closed with precise artifacts and no release overclaim.
