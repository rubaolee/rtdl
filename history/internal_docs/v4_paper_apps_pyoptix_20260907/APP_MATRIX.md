# V4 paper apps / PyOptiX runnable matrix

The denominator is nine project-authored V4 paper applications. The first batch
is an execution priority only; it does not change that denominator. Goal5848's
two synthetic tasks are excluded from this table.

| App | Registered app operation and input | Public application output | Current V4 entry | PyOptiX baseline status | Current execution state |
| --- | --- | --- | --- | --- | --- |
| Particle Tracking | One strict-interior closest-face/cell-transition step; 314,587 vertices, 3,392,530 triangles, 5,000 queries | 5,000 ordered U32x3 `(selected, neighbor, face)` rows | Current public Particle `rtdlexe` lifecycle using the recovered input contract | Code-ready symmetric full-public adapter over the existing public owner; hash-bound prebuilt PTX; device source is semantically matched, not byte-shared | 25-test local suite passes; GPU exact-output dry run not run |
| Graph Triangle Counting | RT-2A1; official SNAP `com-dblp` first, 2,224,385 expected triangles; larger official graphs remain registered scale points | Checked U64 triangle count | `prepare_v4_segmented` / `run_v4_segmented_complete` | Code-ready public triangle GAS/any-hit owner with per-ray `tmax`, device checked-U64 weighted reduction, and hash-bound prebuilt PTX | 25-test local suite passes; PTX/build/output unvalidated on GPU |
| LibRTS | `parks.bz2`, 11,544,398 indexed boxes, 100,000 point and 100,000 range queries | Checked U64 count per `point_contains` and `range_contains` | `prepare_v4_real_scale_count` | Code-ready public custom-AABB owner with exact intersection-program predicate, device U64 count reduction, and hash-bound prebuilt PTX | 25-test local suite passes; PTX/GAS/output unvalidated on GPU |
| RTNN | KITTI-derived 12,000,000 search points, 4,096 queries, K=4 | Ordered query/rank/candidate IDs plus float32 squared distances | `load_real_scale_v4_input` / `prepare_v4` | Multiround distance-window owner missing | Candidate source imports; no baseline |
| X-HD | Stanford Dragon to Happy Buddha, 437,645 by 543,652 points | Directed max-of-nearest witness: exact IDs and tolerance-checked value | `load_real_scale_v4_input` / `prepare_v4` | Multiround nearest/witness owner missing | Candidate source imports; no baseline |
| RT-DBSCAN | Frozen 4,096-point clustered 3-D capacity case | Canonical component labels, core flags and neighbor counts | `load_real_scale_v4_input` / `prepare_v4` | Radius-graph and component-continuation owner missing | Candidate source imports; no baseline |
| RayDB | SSB-SF10 Q1.1, 59,986,052 rows in 12 partitions | Ordered partition/group I64 sums | `run_v4_real_scale_packet` | Partitioned grouped-I64 owner missing | Candidate source imports; cold/full only; private-loader exception retained |
| Spatial RayJoin | County x zipcode top-4 pair, 1,705,027 by 9,982,960 edges, six batches | Six ordered batch result tables and complete-session digest | `compile_v4_real_scale_six_batch` / `run_v4_real_scale_six_batch` | Six-batch planar-overlay owner missing | Candidate source imports; no baseline |
| RT-BarnesHut | 32,768 bodies and 1,486 already-prepared hierarchy nodes | Exact source IDs and tolerance-checked scalar forces | `load_real_scale_v4_input` / `prepare_v4` | Hierarchy-frontier owner missing | Candidate source imports; prepared-hierarchy stage only |

## Interpretation

- `Source/import ready` does not mean CUDA, OptiX, or output parity passed.
- `Complete` names the complete registered stage above. Particle is one query
  step, not 50,000-step advection. Barnes-Hut starts from a prepared hierarchy,
  not tree construction or a multi-step simulation. X-HD is directed unless a
  separately registered reverse direction is executed.
- RayDB has no authentic cross-call prepared owner and therefore receives no
  fabricated prepared row.
- A PyOptiX implementation must use public PyOptiX host APIs and a competent
  device continuation. A slow host-only continuation is not the sole baseline.
- Every absent, invalid, OOM, timeout, or wrong-output row remains in the final
  coverage table.
- `Code-ready` means source, loader, worker, schedule and local contract checks
  exist. It does not mean PyOptiX compiled, output parity passed, or any timing
  is valid on an RT GPU.
- The complete-stage primary timer starts from the already-loaded common domain
  input. Disk input loading is retained as a separate diagnostic and is never
  included in the primary A/C ratio.
- PyOptiX device sources are compiled once before worker zero. The resulting
  PTX bytes, headers, compiler environment, and target architecture are hash
  bound in the config. Their compile time is diagnostic only, not repeatedly
  charged to every PyOptiX worker.
