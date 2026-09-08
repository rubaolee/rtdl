# Remaining application coverage and second-long-workload feasibility

Date: 2026-09-08 America/New_York.

Status: source/data audit only. No new application owner, workload, GPU result,
or performance claim is created by this document. The denominator remains the
nine project-authored V4 paper applications. Particle, triangle counting, and
LibRTS have competent public-PyOptiX comparisons; the six rows below do not.

## 1. Immediate decision

Complete the independently scheduled cit-Patents/4M temporal replication
before starting another application implementation. Do not attempt a second
natural long Particle or LibRTS transaction before the CGO submission unless
the owner explicitly accepts an estimated 6--10 hours of implementation and
GPU-validation risk for Particle. LibRTS is a worse deadline choice.

This recommendation is based on the actual workload boundary:

- The current Particle task has 5,000 queries generated from only four
  barycentric patterns. Increasing the constant repeats positions rather than
  creating a distinct natural workload. A defensible scale extension needs a
  deterministic distinct strict-interior query generator, an independent
  U32x3 oracle, dynamic shape propagation through both arms, and a new RTDL
  artifact. A 1M/5M/20M ladder is only a proposal, not registered evidence.
- LibRTS has 100,000 real point queries and 100,000 real range queries against
  11,544,398 boxes, but prepared query execution is about 0.23 ms in the
  retained transaction. A one-second natural computation would require a very
  large distinct query set. The repository has no such real query file or
  independent oracle, and repeating the existing batch is prohibited.
- Static Particle query plus output storage has a lower bound of 40 bytes per
  query before copies, geometry, GAS, and runtime state. A 20M proposal alone
  therefore accounts for at least 800 MB. LibRTS at hundreds of millions of
  queries is a multi-GB input/output construction problem before index state.

Estimated implementation plus GPU-validation effort is 6--10 hours for a
bounded Particle scale extension and 8--16 hours for a defensible LibRTS scale
extension. These are engineering planning ranges, not measured durations.

## 2. The six unmeasured applications

| Priority | Application | Registered input and public output | Exact missing public-PyOptiX/contract work | Planning range | Submission decision |
| ---: | --- | --- | --- | ---: | --- |
| 1 | RayDB | SSB-SF10 Q1.1; 59,986,052 rows in 12 partitions; ordered partition/group I64 sums | Implement a public partitioned grouped-I64 owner, bind every partition and the ordered result digest, and define an authentic lifecycle endpoint. The recovered V4 route is cold/full only, so a prepared row must not be invented. | 6--10 h | Best post-submission coverage target; not safe to start before the current replication closes. |
| 2 | RTNN | KITTI-derived 12,000,000 search points; 4,096 queries; K=4; ordered query/rank/candidate IDs and f32 squared distances | Implement the same multiround distance-window search in public PyOptiX, preserve stable K-order/tie behavior, retain all rounds, and verify IDs plus consumed-f32 distances. | 8--16 h | High reuse value for nearest/witness mappings, but correctness and tie semantics make it deadline-risky. |
| 3 | X-HD | Stanford Dragon to Happy Buddha, 437,645 by 543,652 points; directed max-of-nearest witness IDs and tolerance-checked value | Reuse only a genuinely generic nearest owner, add directed max/witness continuation, and validate exact witness identities plus tolerance scalar. Do not silently add the reverse direction. | 8--16 h | Follow RTNN if the multiround owner is reusable; otherwise defer. |
| 4 | RT-BarnesHut | 32,768 bodies and 1,486 prepared hierarchy nodes; exact source IDs and tolerance-checked scalar forces | Implement a public hierarchy-frontier owner and same-contract aggregate-frontier continuation. Keep force math app-owned and disclose that the input begins after hierarchy construction. | 10--18 h | Architecturally valuable but less suitable as a quick baseline because traversal, frontier, and tolerance force validation all differ. |
| 5 | RT-DBSCAN | Frozen 4,096-point clustered 3-D capacity case; canonical component labels, core flags, and neighbor counts | Implement public radius-graph discovery plus component continuation and return the full canonical labels/flags/counts. Counting neighbors alone is not the registered output. | 12--24 h | Defer; it combines RT discovery with an iterative connectivity obligation and creates the largest continuation-fairness surface. |
| 6 | Spatial RayJoin | County x zipcode top-4 pair, 1,705,027 by 9,982,960 edges, six batches; six ordered result tables and complete-session digest | First repair the recovered V4 path to return full ordered tables instead of six count/hash summaries, then implement the same public-PyOptiX overlay owner. Both arms currently fail the registered output contract. | 16--30 h | Hard blocker, not merely a missing baseline. Last priority for deadline work despite high long-term value. |

Planning ranges assume an already working CUDA/OptiX/PyOptiX Pod and include
implementation, deterministic oracle checks, local tests, GPU dry runs, and
one evidence-ready transaction. They do not include external review or paper
revision. They must not be presented as empirical measurements.

## 3. Coverage boundary for the paper

The valid paper wording is:

- Nine historical mappings demonstrate design coverage only.
- Three applications currently have competent same-output public-PyOptiX
  performance transactions: Particle, triangle counting, and LibRTS.
- Only triangle counting currently has a natural multi-second prepared task,
  cit-Patents/4M. Its second temporal population is pending.
- The six rows above are unmeasured. Source importability or an RTDL entrypoint
  does not count as a competent-baseline comparison.
- None of the three measured mappings establishes performance for a general
  authored callback. Particle remains shape-specialized; triangle and LibRTS
  use trusted native route components whose scope must be disclosed.

## 4. Required acceptance sequence for any future row

1. Freeze the exact real input, transformation, public output, oracle, and
   physical algorithm used by both arms.
2. Implement a competent public-PyOptiX owner without host-only continuation
   being the sole baseline.
3. Make both arms pass full output parity before any timing run.
4. Perform C-only scale and resource calibration; do not choose scale after
   observing the A/C ratio.
5. Commit source, config, arm artifacts, schedule, threshold, timeout, and
   analysis bytes before formal worker zero.
6. Run eight paired fresh-process blocks, retain every failure/adverse row, and
   independently reconstruct raw evidence without importing project code.
7. Add only the exact measured row to the claim ledger. Do not expand the
   nine-application denominator into nine performance results.

## 5. Source authorities

- `history/internal_docs/v4_paper_apps_pyoptix_20260907/APP_MATRIX.md`
- `history/internal_docs/lead_long_workload_performance_20260908/WORKLOAD_AUDIT.md`
- `history/internal_docs/lead_long_workload_performance_20260908/EXECUTION_DIRECTIVE.md`
- `experiments/v4_paper_apps_pyoptix/contracts.py`
- `experiments/v4_paper_apps_pyoptix/particle_adapter.py`
- `experiments/v4_paper_apps_pyoptix/librts_owner.py`
- `experiments/v4_paper_apps_pyoptix/inputs.py`
