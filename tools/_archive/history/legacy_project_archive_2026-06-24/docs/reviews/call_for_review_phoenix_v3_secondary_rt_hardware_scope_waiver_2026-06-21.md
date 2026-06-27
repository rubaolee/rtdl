# Call For Review: Phoenix V3 Secondary RT Hardware Scope Waiver

Please critically review:

`docs/rebuild/v3/v3_secondary_rt_hardware_scope_waiver_candidate_2026-06-21.md`

Context:

- Phoenix V3 currently has eleven M7-qualified exact row-scoped results.
- The active generic-engine queue is closed.
- The scoped source-tree/pod-gated installer blocker is closed only under
  `source_tree_pod_gated_eleven_row`.
- The remaining secondary hardware blocker exists because `lx1` is GTX 1070 and
  no second RT-core performance platform is available.
- The reachable pod at `root@213.173.108.14 -p 11592`, using
  `id_ed25519_rtdl_codex_current_pod`, is RTX 4000 Ada / driver 550.127.05,
  which is the same hardware class as current M7 evidence, not a second RT
  hardware class.

Review questions:

1. Can this waiver close `secondary_rt_performance_confirmation_not_closed`
   under the explicit scope
   `single_rtx_4000_ada_driver_550_127_05_pod`?
2. Should `secondary_rt_performance_confirmation_authorized` remain `false`
   while `secondary_platform_closes_release_blocker` becomes `true` by reviewed
   waiver?
3. Are the proposed machine-readable fields complete enough for
   `v3_phoenix_secondary_platform_gate.py` and
   `v3_phoenix_release_readiness_gate.py`?
4. What exact P0 amendments, if any, are required before gate implementation?
5. Does the candidate avoid V3 release authorization, broad V3-over-V2 speedup,
   package-install, second-hardware, and multi-GPU portability overclaims?

Please return a verdict using one of:

- `accept-with-amendments-not-release`
- `reject-needs-second-rtx`
- `reject-overclaims`

If accepted, name the exact fields that may flip and the fields that must remain
false.
