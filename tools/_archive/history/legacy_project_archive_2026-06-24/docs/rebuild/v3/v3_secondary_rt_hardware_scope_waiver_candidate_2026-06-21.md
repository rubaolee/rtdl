# V3 Secondary RT Hardware Scope Waiver Candidate

Status: `secondary_rt_hardware_scope_waiver_candidate_pending_external_review`

This candidate asks whether Phoenix V3 may close the secondary RT performance
blocker by explicitly narrowing the release evidence scope to one RTX hardware
configuration instead of claiming second-machine RT-core performance
confirmation.

It does not authorize V3 release, a broad V3-over-V2 speedup claim, package
install wording, or multi-GPU performance portability.

## Current Facts

- The local Linux secondary host `lx1` is a `NVIDIA GeForce GTX 1070`.
- GTX 1070-class hardware has no RT cores.
- The reachable RTX pod is:

```text
host: 2bcb58b259e4
gpu: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
memory: 20475 MiB
pci_bus_id: 00000000:C1:00.0
ssh: root@213.173.108.14 -p 11592
key: id_ed25519_rtdl_codex_current_pod
```

- The reachable pod is the same RTX 4000 Ada / driver 550 class as the current
  Phoenix V3 M7 evidence.
- It is not a second RT-core hardware class.
- The current eleven M7-qualified rows are exact row-scoped results, not broad
  app, paper, or V3-over-V2 speedup claims.
- The scoped installer/reproducibility blocker is closed only under
  `source_tree_pod_gated_twelve_row`.

## Proposed Machine-Readable Scope

```text
release_scope: source_tree_pod_gated_twelve_row
hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod
secondary_rt_performance_confirmation_authorized: false
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
multi_gpu_performance_portability_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_authorized: false
```

## Allowed Wording If Reviewed

```text
Phoenix V3 performance evidence is scoped to eleven exact M7 rows measured on a
single NVIDIA RTX 4000 Ada Generation pod with driver 550.127.05, reproducible
from the source tree through the documented pod-gated environment. Secondary
Linux compatibility was checked on lx1 / GTX 1070, but no second RT-core
performance platform is claimed.
```

## Forbidden Wording

```text
V3 performance is confirmed across RT-core GPUs.
V3 is portable across RTX hardware.
V3 broadly beats V2.x.
V3 has second-machine RT-core performance confirmation.
V3 has a general package installer.
```

## Non-Closure

Even if this waiver is accepted, Phoenix V3 remains `blocked_not_release` until
a new aggregate release-readiness review explicitly supersedes the prior
release-readiness consensus and decides whether the scoped twelve-row surface is
enough for the intended V3 release shape.

This waiver only targets the blocker named:

```text
secondary_rt_performance_confirmation_not_closed
```

It does not close:

```text
release_authorization_false
twelve_row_surface_still_too_narrow_for_major_release
missing_point_location_topology_stream_m7_capability_family
twelve_row_release_readiness_consensus_blocks_release
```

The later aggregate release-readiness review reclassifies broad V3-over-V2
speedup as a forbidden claim constraint, not a separate scoped-release P0,
while `broad_v3_faster_than_v2_claim_authorized: false` stays false.

## Required External Review Questions

1. Is the single-RTX hardware scope explicit enough to close the secondary RT
   blocker without implying second-machine RT-core performance confirmation?
2. Are the proposed machine-readable fields sufficient for the release gate?
3. Should `secondary_rt_performance_confirmation_authorized` remain `false`
   while `secondary_platform_closes_release_blocker` becomes `true` by waiver?
4. What wording or gate changes are required before this candidate can be
   accepted?
5. Does this candidate preserve `release_authorized: false` and block broad
   V3-over-V2 claims?

## Goal-Level Decision Audit

Decision: seek review for a hardware-scoped waiver instead of pretending the
reachable RTX 4000 Ada pod is a second RT hardware platform.

1. Was I foolish?
   No. The foolish earlier path was using the wrong SSH key and then treating
   pod access as unavailable; after using `id_ed25519_rtdl_codex_current_pod`,
   the pod is reachable, but it is still the same RTX 4000 Ada evidence class.
2. If yes, what actions made the decision foolish?
   Not applicable for this decision. The foolish action would be to call this
   reachable pod a second hardware class or to let waiver wording imply
   multi-GPU portability.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. A true second RTX-class machine could rerun the twelve rows or a
   reviewed calibrated subset. That remains stronger evidence, but it is not
   currently available in the known machine set.
4. Can I now try a different path that actually solves the problem?
   Yes. Record a strict single-hardware release scope, ask Claude for external
   review, and only update gates if the review accepts that this closes the
   secondary blocker under waiver while keeping V3 unreleased.
