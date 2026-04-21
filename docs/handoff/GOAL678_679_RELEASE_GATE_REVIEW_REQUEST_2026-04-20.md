# Goal678/679 Release Gate Review Request

Please review the current RTDL local and Linux release-gate evidence after the
cross-engine prepared/prepacked visibility/count optimization round.

Return `ACCEPT` or `BLOCK`. If accepted, confirm that the release-gate evidence
is sufficient for the current optimization round and that the claim boundaries
are honest. If blocked, identify the exact file, command, or claim that must be
fixed.

Primary reports:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal678_local_total_test_doc_flow_audit_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal679_linux_gpu_backend_release_gate_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal679_linux_gpu_backend_release_gate_2026-04-20.json`

Preceding closure/consensus:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal676_677_cross_engine_optimization_closure_and_doc_refresh_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal676_677_consensus_2026-04-20.md`

Evidence summary:

- Local full suite: `1266` tests OK, `187` skips.
- Public command truth audit: valid, `250` commands across `14` docs.
- Public entry smoke: valid.
- Focused public-doc tests: `10` tests OK.
- `git diff --check`: clean.
- Linux fresh sync path: `/tmp/rtdl_goal679`.
- Linux builds from fresh synced source:
  - OptiX: PASS, version `(9, 0, 0)`.
  - Vulkan: PASS, version `(0, 1, 0)`.
  - HIPRT: PASS, version `(2, 2, 15109972)`.
- Linux focused native suite:
  - `30` tests OK, `2` Apple RT skips.
- Linux performance sanity, `4096` rays / `1024` triangles:
  - OptiX direct `0.0035153299977537245 s`, prepared/prepacked
    `0.00005833699833601713 s`.
  - HIPRT direct `0.5688568009936716 s`, prepared
    `0.0057718300085980445 s`.
  - Vulkan direct `0.009350006002932787 s`, prepared/prepacked
    `0.004641148989321664 s`.

Boundaries to verify:

- GTX 1070 has no RT cores; Linux OptiX/Vulkan timing is not RT-core evidence.
- HIPRT evidence is HIPRT/Orochi CUDA on NVIDIA, not AMD GPU validation.
- The performance sanity is repeated 2D visibility/any-hit/count evidence, not
  DB or graph evidence.
- Prepared/prepacked paths use narrower or more compact output contracts than
  general full emitted-row workloads.
- Apple RT is not validated by the Linux gate; it was covered by earlier local
  Apple M4 gates.
