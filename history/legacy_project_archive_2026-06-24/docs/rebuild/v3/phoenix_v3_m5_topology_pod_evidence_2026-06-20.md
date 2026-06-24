# Phoenix V3 M5 Topology Pod Evidence

Date: 2026-06-20

Status: internal evidence passed with RayJoin author-code comparison recovered.

Artifact directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620
```

## Verdict

M5 produced usable internal V3 topology evidence on RTX hardware, including a
RayJoin author `query_exec` comparison for the PIP point-location row. It is
still not release evidence and not paper reproduction.

```text
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
m5_author_code_comparison_status: complete
overall_status: internal_evidence_with_author_code
status_label: internal-author-complete
```

RayJoin author `query_exec` was rebuilt from upstream source
`rubaolee/RayJoin` at commit `02bf6220d6d20b04af77ee20364eced75cc029c9` on the
RTX 4000 Ada pod. The build required CUDA 12.8 compatibility shims already used
in earlier RayJoin goals: `src/util/markers.h` includes
`nvtx3/nvToolsExt.h`, `src/CMakeLists.txt` targets SM 89, and PTX compilation
receives the glog/gflags include paths. The build evidence is saved under
`docs/rebuild/v3/evidence/rayjoin_author_build_20260620`.

## Gates

- GPU Python env gate: pass.
- OptiX/RT hardware gate: pass on NVIDIA RTX 4000 Ada Generation, driver
  550.127.05, compute capability 8.9.
- M5 local graph gate: pass, with `topology_face_contract_v1` and
  `continuation.compact_mask`.
- `query_exec` bounded preflight: recovered as
  `/workspace/RayJoin_fresh/release/bin/query_exec`.
- Intake: pass, with author-code comparison complete and all release/public
  flags false.

## PIP Point-Location

Workload:

- base CDB: `data/rayjoin_public_cdb/br_county.cdb`;
- query points: 100,000;
- query generation: backend-parity-filtered random bbox;
- artifact label: `m5_pip_point_location_parity_filtered_100k`;
- parity filter rejected 1 exact-row tie candidate before timing;
- OptiX repeats: 1000;
- Embree repeats: 1000;
- RayJoin author repeats: 1000;
- timed output: scalar positive-face count;
- row materialization in timed path: false.

Correctness:

- OptiX rows: 100,000;
- Embree rows: 100,000;
- exact `(point_id, face_id, segment_id)` mismatches: 0;
- positive face count: 43,738 on both backends.

Internal and author timing:

| Row | Median Hot Query | Native Traversal Median | Ratio |
| --- | ---: | ---: | ---: |
| RayJoin RT author `query_exec` | 0.000470 s | n/a | 5.728x faster than RTDL OptiX wall median |
| RTDL OptiX | 0.002693 s | 0.001815 s | 1.920x faster than RTDL Embree |
| RTDL Embree | 0.005170 s | 0.005144 s | baseline |

Native traversal ratio: OptiX is 2.834x faster than Embree for this filtered
same-contract point-location row.

Interpretation: this is internal RTDL OptiX/Embree same-contract topology
evidence plus an author-code timing basis. RayJoin author RT is faster than
RTDL OptiX on this row, so this evidence does not support an "RTDL beats
RayJoin" claim. It supports the narrower V3 language claim that RTDL can express
the same point-location topology contract and that its OptiX lowering beats its
Embree lowering on the RTX pod.

Timing basis caveat: RayJoin's 0.470115 ms value is the internal C++ `Query`
timer parsed from `query_exec` stdout. RTDL OptiX/Embree hot medians are Python
`time.perf_counter` measurements around `count_positive_faces`, including Python
dispatch and scalar count-return overhead. The narrower native-traversal
comparison is RayJoin Query vs RTDL OptiX native traversal: RayJoin is 3.861x
faster on that basis. Neither number is a RayJoin paper-reproduction claim.

## Overlay Active Count

Workload:

- left CDB: `br_county_start256_count512.cdb`;
- right CDB: `br_soil_start256_count512.cdb`;
- output contract: `overlay_active_pair_dependency_count`;
- warmup: 2;
- repeat: 25.

Correctness:

- active count: 174;
- OptiX and Embree active counts match;
- row materialization avoided in timed path;
- old raw relation-row contract is explicitly rejected as not comparable.

Internal timing:

| Row | Median | Native Traversal Median | Internal Ratio |
| --- | ---: | ---: | ---: |
| RTDL OptiX | 0.000203 s | 0.000203 s | 499.112x vs RTDL Embree |
| RTDL Embree | 0.101092 s | 0.100408 s | baseline |

Interpretation: this is internal same-contract active-count topology evidence.
It does not authorize full polygon overlay, RayJoin section reproduction, or
public speedup wording.

## Failed Attempts Preserved On Pod

Four failed/partial/recovery attempts were preserved before the final
author-code-complete parity-filtered run:

- `phoenix_v3_m5_topology_20260620_failed_markdown_none_20260620T173923Z`
  captured the missing-author Markdown bug.
- `phoenix_v3_m5_topology_20260620_failed_pip_tie_mismatch_20260620T175119Z`
  captured the unfiltered random stream with one exact-row tie mismatch.
- `phoenix_v3_m5_topology_20260620_stopped_unbounded_query_exec_find_20260620T174322Z`
  captured the stopped unbounded `query_exec` search attempt.
- `m5_query_exec_author_recovery_20260620T181810Z.log` captured the first
  author-code recovery rerun that correctly ran `query_exec` but failed intake
  because it reused an existing query CDB without writing parity-filter
  provenance into the summary.

Those failures are part of the evidence trail. The current accepted artifact is
the parity-filtered run pulled into the local evidence directory above.

## Goal-Level Decision Audit

Decision: accept M5 as internal author-code-complete evidence, while keeping
release and public speedup claims blocked until M7.

1. Was I foolish?

   The earlier unbounded `query_exec` search, the unfiltered "safe100k"
   wording, and the first author recovery rerun without parity-filter
   provenance were foolish. They wasted pod time and risked ambiguous evidence.

2. What actions made it foolish?

   I used a broad `/workspace /root` `find` without timeout, reused
   "safe100k" language, and initially reran author code against an existing CDB
   without regenerating the parity-filter report.

3. Was there another path?

   Yes. The correct path was bounded preflight, rebuild `query_exec` from the
   upstream RayJoin source using the known CUDA 12.8 compatibility shims, then
   rerun with backend-parity filtering before timing.

4. Can I now try a different path that actually solves the problem?

   Yes. That path has now been executed. The next solving path is not to declare
   release success; it is to feed this row into an M7 packet with row-level
   public-claim review, or keep it internal.
