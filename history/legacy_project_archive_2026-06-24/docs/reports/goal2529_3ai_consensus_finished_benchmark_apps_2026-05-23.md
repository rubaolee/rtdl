# Goal2529: 3-AI Consensus For Finished Benchmark Apps

Date: 2026-05-23

## Decision

Final verdict: `ACCEPT-WITH-BOUNDARY`.

Codex, Claude, and Gemini agree that the five current RTDL research benchmark
apps can be treated as finished for their scoped reconstruction purposes:

- Hausdorff/X-HD-style
- Spatial RayJoin-style
- RT-DBSCAN-style
- Robot-collision-style
- RayDB-style

This consensus does not authorize release tagging, package-install support, full
paper reproduction claims, authors-code parity claims, whole-app speedup claims,
or broad public performance wording.

## Review Inputs

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2529_finished_benchmark_apps_consensus_packet_2026-05-23.md` | `ACCEPT-WITH-BOUNDARY` |
| Claude | `docs/reports/goal2529_claude_review_finished_benchmark_apps_2026-05-23.md` | `ACCEPT` |
| Gemini | `docs/reports/goal2529_gemini_review_finished_benchmark_apps_2026-05-23.md` | `ACCEPT-WITH-BOUNDARY` |

Claude found no blocker and explicitly accepted the classification and claim
boundaries. Gemini accepted the classification with wording constraints. Those
constraints are adopted below.

## Adopted Constraints

All future docs and catalog entries should follow these constraints unless a
later reviewed goal supersedes them:

- Label these apps as `research benchmarks` or `reconstruction instruments`,
  not full products or complete paper reproductions.
- When citing Hausdorff performance, state that current-main/v2.1 performance
  refresh is pending and that the May 16 evidence is the applicable reviewed
  timing set.
- Limit performance language to exact-subpath evidence for reviewed datasets,
  commands, hardware, and artifacts.
- Explicitly disclaim authors-code parity, full paper reproduction, and broad
  speedup wins.
- Keep native Embree/OptiX paths app-name-free. Use generic primitive wording
  such as grouped integer statistics, fixed-radius graph continuation, grouped
  finite segment any-hit flags, prepared spatial relationship queries, and
  point-group witness reductions.

## Finished-App Classification

| App | Consensus status | Authorized wording | Blocked wording |
| --- | --- | --- | --- |
| Hausdorff/X-HD-style | Finished as exact 2D projected-point reconstruction app | RTDL can express exact 2D projected-point Hausdorff with Python-owned X-HD-style policy over generic RTDL point-group threshold and witness primitives | Full X-HD reproduction, full 3D surface Hausdorff, MRI/BraTS reproduction, universal CUDA-vs-RT speedup, fresh current-main replacement timing |
| Spatial RayJoin-style | Finished as scoped LSI/PIP RTDL benchmark app | RTDL can express scoped RayJoin-style LSI/PIP workloads using generic prepared spatial primitives | RTDL beats RayJoin, full RayJoin paper reproduction, whole-app speedup |
| RT-DBSCAN-style | Finished as generic fixed-radius graph/component benchmark app | RTDL has generic fixed-radius rows, threshold columns, adjacency streams, and grouped continuation sufficient for the scoped app | Paper reproduction, paper-level speedup, broad DBSCAN acceleration, native DBSCAN ABI |
| Robot-collision-style | Finished as sampled static-scene feasibility-screening benchmark app | RTDL has generic grouped finite 3D segment probes, prepared static-scene reuse, reusable query buffers, compact flags, and count-only screening | General robot-collision solver, continuous/swept collision, exact solid contact, robot-specific native ABI |
| RayDB-style | Finished as deterministic columnar grouped-aggregate benchmark app | RTDL has generic partner-resident columnar descriptors and fused grouped integer statistics for the scoped grouped aggregate contract | RayDB paper reproduction, SQL/DBMS implementation, SSB reproduction, authors-code comparison, broad DB speedup |

## Consensus Conclusion

The benchmark-app program has produced five closed reconstruction instruments.
Each app exposed a reusable language/runtime pressure point, and each closeout
kept paper/application semantics outside the native engine.

Future work should use these apps as evidence-backed design pressure, not as
full external-system reproductions. Any new public speedup wording, authors-code
comparison, or paper-facing claim still needs a separate exact-scope evidence
packet and external review gate.
