# V3 Secondary Platform Strategy

Status: `compatibility_confirmed_hardware_scope_waiver_reviewed_not_release`

This packet classifies the local Linux host evidence and the reviewed
single-hardware waiver for Phoenix V3. It does not authorize a V3 release, a
broad V3-over-V2 speedup claim, package-install wording, multi-GPU performance
portability, or any second-machine RT-core performance claim.

## Decision

`lx1` / `192.168.1.20` is accepted only as a secondary compatibility and
reproducibility host.

It is not accepted as a second RT performance platform for V3 public speed
claims because the recorded GPU is:

```text
NVIDIA GeForce GTX 1070
```

GTX 1070-class hardware has no RT cores. It can confirm source-tree,
dependency, wording, CUDA partner smoke, and non-release reproducibility
properties, but it cannot confirm RTX/RT-core performance portability.

The secondary RT release blocker is closed only by a reviewed hardware-scoped
waiver:

```text
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod
secondary_rt_performance_confirmation_authorized: false
multi_gpu_performance_portability_claim_authorized: false
release_authorized: false
```

The waiver reviews are:

```text
docs/reviews/claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md
Verdict: accept-with-amendments-not-release
docs/reviews/codex_phoenix_v3_secondary_rt_hardware_scope_waiver_2ai_consensus_2026-06-21.md
Status: claude_codex_consensus_secondary_rt_hardware_scope_waiver_not_release
```

The reachable RTX pod fingerprint is:

```text
host: 2bcb58b259e4
gpu: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
memory: 20475 MiB
pci_bus_id: 00000000:C1:00.0
scope: single_rtx_4000_ada_driver_550_127_05_pod
```

## Evidence

Current local evidence directories:

```text
docs/rebuild/v3/evidence/v3_all_benchmark_lx1_confirmation_20260620
docs/rebuild/v3/evidence/v3_paired_report_lx1_confirmation_20260620
docs/rebuild/v3/evidence/v3_second_machine_lx1_confirmation_20260620
```

What they prove:

- `v3_rebuild_matrix.json`: selected V3 rebuild tests passed on `lx1`.
- `source_tree_doctor.json`: required source-tree checks passed.
- `wording_gate.json`: the Phoenix wording gate passed.
- `gpu_env_gate_summary.json`: CuPy, PyTorch CUDA, and Numba CUDA smoke gates
  passed in the second-machine confirmation directory.

What they do not prove:

- They do not rerun the full all-app performance suite on `lx1`.
- They do not rerun the paired V2.14-vs-current-V3 performance suite on `lx1`.
- They do not provide RT-core performance confirmation.
- They do not provide second-machine RT-core performance confirmation.
- They do not prove multi-GPU performance portability.

What the reviewed waiver proves:

- the missing second-machine evidence is explicitly excluded from the V3
  performance scope;
- V3 row-scoped performance wording is limited to the single RTX 4000 Ada pod
  scope above;
- the secondary RT blocker can close under this scope while
  `secondary_rt_performance_confirmation_authorized` remains `false`.

## Machine Gate

Run:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_secondary_platform_gate.py --pretty
```

Expected current status:

```text
status: compatibility_confirmed_hardware_scope_waiver_reviewed_not_release
secondary_compatibility_confirmed: true
secondary_rt_performance_confirmation_authorized: false
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod
multi_gpu_performance_portability_claim_authorized: false
release_authorized: false
```

## Release Consequence

The second-machine RT evidence is still absent, but the release blocker is
closed under the single RTX 4000 Ada hardware scope by the Claude/Codex-reviewed
waiver. This is a blocker closure by scope, not by evidence broadening.

The remaining release work is:

1. request a new aggregate release-readiness review that explicitly covers the
   thirteen-row surface, scoped installer closure, and hardware waiver;
2. decide whether the narrow source-tree/pod-gated thirteen-row surface is enough
   for the intended V3 release shape;
3. keep broad V3-over-V2, package-install, second-hardware, and portability
   claims unauthorized.

Until that aggregate review happens, Phoenix V3 remains `blocked_not_release`.

## Goal-Level Decision Audit

Decision: classify `lx1` / GTX 1070 as compatibility confirmation, and close
the secondary RT blocker only by Claude/Codex-reviewed single-RTX
hardware-scope waiver.

1. Was I foolish?
   No. The decision prevents non-RT hardware or the reachable RTX 4000 Ada pod
   from being misread as second-machine RT-core performance confirmation.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be treating `lx1` passing tests,
   wording, doctor, CUDA partner smoke gates, or a same-class RTX 4000 Ada pod
   as proof of multi-GPU RTX/OptiX performance portability.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: run a true second RTX-class machine and review the twelve rows or a
   calibrated subset. That remains stronger evidence, but it is not currently
   available in the known machine set.
4. Can I now try a different path that actually solves the problem?
   Yes. Use the reviewed single-hardware waiver to close only the secondary
   blocker, then require aggregate release-readiness review before any release
   authorization.
