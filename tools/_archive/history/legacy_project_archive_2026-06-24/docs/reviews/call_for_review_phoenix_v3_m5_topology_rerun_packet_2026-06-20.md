# Call For Review: Phoenix V3 M5 Topology Rerun Packet

Date: 2026-06-20

Reviewer: Claude

## Request

Please critically review the Phoenix V3 M5 topology rerun packet before pod
execution. The goal is not release promotion. The goal is to decide whether
this packet is a responsible next V3-only evidence run under Goal4392 M5.

Answer with:

1. verdict: approve, approve with amendments, or reject;
2. P0/P1 issues;
3. specific amendments required before pod execution;
4. whether the packet correctly keeps V3 release/public speedup claims blocked;
5. whether the packet handles the missing RayJoin author `query_exec` binary
   honestly.

## Governing V3 Plan

Goal4392 defines M5 as:

> RayJoin point-location/topology pilot: Express PIP and overlay through generic
> face-id, point-location, compact, and topology streams.

M5 exit condition:

> Author code, RTDL OptiX, and RTDL Embree compared under same CDB
> point-location/topology contract and separated timing bases; same-contract
> measurements taken on hardware with OptiX-capable GPU and M3-grade phase
> accounting.

Public V3 performance claims remain blocked until M7 release-grade benchmark
harness and external review.

## Packet Summary

Packet paths:

- `docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.json`

Status:

```text
ready_for_external_review_not_executed
goal4392_gate: M5
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

Primary generic capabilities:

- `point_location_topology_stream`
- `compact_positive_stream`

Known blocker:

- Current pod preflight did not find RayJoin author `query_exec`.
- If `query_exec` remains missing, the packet records M5 author-code completion
  as blocked and runs only RTDL same-contract internal evidence.
- Missing `query_exec` is classified as an author-code availability blocker,
  not a failure of V3 topology code.

Remote target:

```text
ssh root@213.173.108.14 -p 11592 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
cd /root/rtdl_v3_rebuild_20260620/current
ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m5_topology_20260620
PY=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

Required commands:

- record `nvidia-smi`, `VERSION`, and GPU Python env gate;
- build Embree and OptiX native libraries;
- run `rt.validate_m5_topology_pilots()`;
- search `/workspace` and `/root` for `query_exec`;
- run `scripts/goal4373_rayjoin_cdb_point_location_compare.py` with
  `--point-count 100000`, `--correctness-sample 100000`,
  `--rtdl-repeats 1000`, `--optix-repeats 10000`, `--embree-repeats 1000`;
- run `scripts/v3_0_m33_rayjoin_overlay_active_count_same_contract.py` on the
  512x512 CDB slice.

Acceptance checks:

- all outputs preserved under the artifact directory;
- graph gate passes;
- `query_exec` status recorded as `present` or `missing`;
- PIP rows record RTDL OptiX and RTDL Embree under the same point-location
  contract;
- overlay active-count rows record RTDL OptiX and RTDL Embree under
  `overlay_active_pair_dependency_count`;
- if `query_exec` is missing, M5 author-code completion is marked blocked;
- full polygon overlay, RayJoin paper reproduction, public speedup, and release
  authorization remain false.

Failure policy:

- preserve failed artifacts;
- no scale-down without a new packet;
- no public claim from partial success;
- `query_exec` missing is a blocker, not an RTDL topology failure.

## Local Gates Already Run

```text
py -3 -m unittest tests.v3_phoenix_m5_topology_packet_test tests.v3_release_wording_gate_test
Result: 5 tests OK

py -3 scripts\v3_release_wording_gate.py --pretty
Result: pass, no violations

py -3 scripts\run_test_matrix.py --group v3_rebuild
Result: 13 modules, 48 tests OK
```

## Goal-Level Decision Audit

Decision under review: proceed from local M5 packet to external review and then,
if approved, execute on the pod.

1. Was I foolish?

   No, provided this remains V3-only internal evidence and not release wording.

2. If yes, what actions would make it foolish?

   It would be foolish to treat missing `query_exec` as solved, call same-contract
   RTDL-only rows a complete RayJoin paper reproduction, or publish speedups
   before M7.

3. Was there another path that would avoid getting stuck?

   Yes. If this packet is too weak, the safer path is to amend it with stronger
   provenance/phase-accounting checks before pod execution, or switch to M6
   only after recording M5 as blocked.

4. Can I now try a different path that actually solves the problem?

   Yes. The packet is designed to either produce honest M5 internal evidence or
   record a precise blocker, rather than inventing success.
