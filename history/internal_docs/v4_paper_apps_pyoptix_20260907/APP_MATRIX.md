# V4 paper apps / PyOptiX runnable matrix

The denominator is nine project-authored V4 paper applications. The first batch
is an execution priority only; it does not change that denominator. Goal5848's
two synthetic tasks are excluded from this table.

| App | Registered app operation and input | Public application output | Current V4 entry | PyOptiX baseline status | Current execution state |
| --- | --- | --- | --- | --- | --- |
| Particle Tracking | One strict-interior closest-face/cell-transition step; 314,587 vertices, 3,392,530 triangles, 5,000 queries | 5,000 ordered U32x3 `(selected, neighbor, face)` rows | Recovered app `prepare_v4`: public prepared callback owner with ordinary restricted-callback compilation; not the `rtdlexe` lifecycle | Symmetric full-public adapter over the existing public owner; hash-bound prebuilt PTX; device source is semantically matched, not byte-shared | Final `c5c8be48b` exact-output dry run and all formal cells pass; complete/first/prepared medians are adverse at 10.208x/75.533x/37.928x V4/PyOptiX |
| Graph Triangle Counting | RT-2A1; official SNAP `com-dblp` first, 2,224,385 expected triangles; larger official graphs remain registered scale points | Checked U64 triangle count | `prepare_v4_segmented`: standard callback through the general Numba-leaf device-column entry, followed by CuPy checked-U64 weighted reduction; `fast_control` specialization is not used | Public triangle GAS/any-hit owner with per-ray `tmax`, device checked-U64 weighted reduction, and hash-bound prebuilt PTX | Final `c5c8be48b` exact-output dry run and all formal cells pass; complete/first/prepared medians are adverse at 3.411x/2.732x/1.379x V4/PyOptiX |
| LibRTS | `parks.bz2`, 11,544,398 indexed boxes, 100,000 point and 100,000 range queries | Checked U64 count per `point_contains` and `range_contains` | `prepare_v4_real_scale_count`; generic prepared index/query handles and device scalar count reduction | Public custom-AABB owner with exact intersection-program predicate, device U64 count reduction, hash-bound prebuilt PTX, and symmetric prepared query residency | Four separate 192-worker transactions pass and independently recount. Final point ratios are 1.312x/12.059x/38.467x and range ratios are 1.080x/13.422x/39.083x for complete/first/prepared; device reduction did not close the physical-route debt |
| RTNN | KITTI-derived 12,000,000 search points, 4,096 queries, K=4 | Ordered query/rank/candidate IDs plus float32 squared distances | `load_real_scale_v4_input` / `prepare_v4` | Multiround distance-window owner missing | Candidate source imports; no baseline |
| X-HD | Stanford Dragon to Happy Buddha, 437,645 by 543,652 points | Directed max-of-nearest witness: exact IDs and tolerance-checked value | `load_real_scale_v4_input` / `prepare_v4` | Multiround nearest/witness owner missing | Candidate source imports; no baseline |
| RT-DBSCAN | Frozen 4,096-point clustered 3-D capacity case | Canonical component labels, core flags and neighbor counts | `load_real_scale_v4_input` / `prepare_v4` | Radius-graph and component-continuation owner missing | Candidate source imports; no baseline |
| RayDB | SSB-SF10 Q1.1, 59,986,052 rows in 12 partitions | Ordered partition/group I64 sums | `run_v4_real_scale_packet` | Partitioned grouped-I64 owner missing | Candidate source imports; cold/full only; private-loader exception retained |
| Spatial RayJoin | County x zipcode top-4 pair, 1,705,027 by 9,982,960 edges, six batches | Registered target: six ordered batch result tables and complete-session digest. Current recovered V4 app returns only six count/hash summaries, so it does not yet satisfy this output contract. | `compile_v4_real_scale_six_batch` / `run_v4_real_scale_six_batch`; current output is summary-only | Six-batch planar-overlay full-output owner missing | Blocked before comparison: neither the current V4 entry nor a PyOptiX owner exposes the registered full row-table result |
| RT-BarnesHut | 32,768 bodies and 1,486 already-prepared hierarchy nodes | Exact source IDs and tolerance-checked scalar forces | `load_real_scale_v4_input` / `prepare_v4` | Hierarchy-frontier owner missing | Candidate source imports; prepared-hierarchy stage only |

## Interpretation

- `Source/import ready` does not mean CUDA, OptiX, or output parity passed.
- `Complete` names the complete registered stage above. Particle is one query
  step, not 50,000-step advection. Barnes-Hut starts from a prepared hierarchy,
  not tree construction or a multi-step simulation. X-HD is directed unless a
  separately registered reverse direction is executed.
- RayDB has no authentic cross-call prepared owner and therefore receives no
  fabricated prepared row.
- RayJoin count/hash summaries are validation metadata, not complete row-table
  outputs. That row remains blocked until both arms expose the registered full
  result; no summary-only timing may enter the application comparison table.
- A PyOptiX implementation must use public PyOptiX host APIs and a competent
  device continuation. A slow host-only continuation is not the sole baseline.
- Every absent, invalid, OOM, timeout, or wrong-output row remains in the final
  coverage table.
- `Code-ready` means source, loader, worker, schedule and local contract checks
  exist. It does not mean PyOptiX compiled, output parity passed, or any timing
  is valid on an RT GPU.
- The first three rows now have a final frozen RTX A4500 transaction at source
  `c5c8be48b`; all ratios are adverse and none authorizes a public or manuscript
  performance claim. The remaining six rows have no frozen competent PyOptiX
  owner and remain unexecuted rather than being removed from the denominator.
- The complete-stage primary timer starts from the already-loaded common domain
  input. Disk input loading is retained as a separate diagnostic and is never
  included in the primary A/C ratio.
- PyOptiX device sources are compiled once before worker zero. The resulting
  PTX bytes, headers, compiler environment, and target architecture are hash
  bound in the config. Their compile time is diagnostic only, not repeatedly
  charged to every PyOptiX worker.
