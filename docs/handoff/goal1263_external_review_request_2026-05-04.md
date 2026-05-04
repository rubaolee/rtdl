# Goal1263 External Review Request

Date: 2026-05-04

Please review the v1.1 Embree/OptiX performance interpretation in:

- `docs/reports/goal1262_v1_1_patched_full_matrix_intake_2026-05-04.md`
- `docs/reports/goal1263_polygon_pair_scale_sweep_intake_2026-05-04.md`

Context:

- RTDL v1.0 is released.
- v1.1 is post-release hardening and Embree/OptiX triage.
- Before v2.1, Vulkan/HIPRT/Apple RT are not active implementation targets.
- NVIDIA RT performance is the top priority.
- Public/release/major performance conclusions require 3-AI consensus.

Questions:

1. Is the Goal1262 interpretation correct that DB is execution-unblocked but
   not public-speedup-ready, graph and Jaccard remain correctness-ready but
   slower, and polygon-pair is the strongest positive candidate?
2. Does Goal1263 provide enough same-contract evidence to treat
   `polygon_pair_overlap_area_rows` as a bounded positive OptiX performance
   candidate for external review?
3. Is the proposed boundary acceptable: RT-assisted LSI/PIP positive candidate
   discovery plus native C++ exact area continuation, not monolithic GPU
   polygon overlay, not whole-app speedup, and not broad GIS acceleration?
4. Is `candidate_count_matches_expected: false` acceptable when summary parity
   is true under the current profiler contract, or should this block any
   positive wording until diagnostics are reconciled?
5. What exact allowed and disallowed wording should be used if this is accepted?

Requested output:

- Verdict: ACCEPT, ACCEPT WITH CHANGES, or REJECT.
- Required changes before consensus, if any.
- Exact allowed wording.
- Exact blocked wording.
- Any additional tests or pod reruns required before public docs change.
