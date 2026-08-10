# Paper Reproduction Apps

This directory holds RTDL programs that reproduce selected workloads from
published papers. It is a separate line from the promoted benchmark apps:

RTDL 3.0 functionally qualifies nine paper applications. Paper algorithms and
comparators remain application-owned; V3 resolves and verifies their registered
physical regions and never chooses between distinct paper algorithms.

- benchmark apps exercise RTDL language/runtime development across the current
  10-app portfolio;
- paper reproduction apps follow a paper's workload contract as closely as the
  available inputs, author code, and documented comparator allow.

Each paper gets its own subdirectory. Current apps:

| Paper app | RTDL language surface exercised | Bounded reproduction status | Performance status | Boundary |
| --- | --- | --- | --- | --- |
| [RayJoin paper](rayjoin-paper/README.md) | Public planar-map LSI/PIP primitives, device-columnar rows, ordering, and writer-free binary operators. | Available-pair bounded Section 5.2 LSI and Section 5.3 PIP, plus bounded Section 5.7 overlay reproduction, are complete. | Final v2.14.4 prepared-binary top4 evidence is `0.328842s` for six distinct batches; the comparable AuthorOfficial core phases are `0.187042s` (`1.76x` slower RTDL under this bounded boundary). | Not a broad all-input RayJoin performance claim; binary descriptors and author polygons have different semantics. |
| [RT-BarnesHut paper](rt-barneshut-paper/README.md) | Generic `AggregateHierarchy3D`, opening policies, reducers, CPU reference executor, and optional Numba parity executor. | Bounded same-input prepared-state scalar force-output reproduction against the pinned AuthorOfficial comparator. | Narrow resident-kernel phase is phase-boundary-limited; broader reported envelope remains unfavorable to RTDL. | Not full paper reproduction; independent tree construction is not claimed. |
| [RT-DBSCAN paper](rt-dbscan-paper/README.md) | Generic fixed-radius count-threshold primitives plus app-owned DBSCAN component continuation. | Bounded AuthorOfficial same-input gates and a three-fixture representative synthetic partition matrix are complete. | Cold and warm diagnostics are retained separately; no paper-performance claim is authorized. | Exact paper preprocessing is unavailable, and RTDL does not adopt the author's index-directional border semantics. |
| [X-HD paper](x-hd-paper/README.md) | Generic candidate-row, nearest-witness, max-nearest reduction, cell-MBR, and partner exact-witness routes. | Same-input directed input1-to-input2 `HDResult` reproduction is complete and externally approved across seven primary cases. | Author internal, author process-wall, RTDL fresh, and RTDL warm timings remain separate; no ratio is authorized. | Not exact paper-input, all-figure, author RT-core algorithm, or performance reproduction. |
| [LibRTS paper](librts-paper/README.md) | Generic prepared/mutable 2-D AABB queries, sparse native refit, rollback/fail-closed mutation, and operation-scoped packed-AABB semantics. | Externally approved scoped closeout: exact point-contains and range-contains count matrices are each 14/14; representative PIP has 71,626 canonical relation rows equal; bounded mutation counts match at `[2,1,0,1,0]`. | No author-versus-RTDL paper-performance ratio is authorized; sparse-refit numbers are RTDL system diagnostics only. | Range-intersects remains 14 matches, 2 author capacity failures, and 26 uncheckpointed. Full-paper/Figure reproduction, complete range-intersects coverage, author algorithm equivalence, count-case pointwise equality, zero-copy, and Embree remain unclaimed. |
| [RTNN paper](rtnn-paper/README.md) | Generic open/closed radius semantics, CUBIN-cache hardening, borrowed relation columns, and prepared ranked distance-window Q*K output. | Externally approved scoped closeout: exact relations match bounded, representative, public same-source, and a 12M-search/4,096-query Level-B same-byte gate under exact float32 tie classes. Author default mode 2 has score recall@K `1.0` on that one workload. | Same-POD RTDL old-route/new-route query diagnostic: `783.417830s -> 2.244261s` median (~349.08x) with ~39,457x fewer materialized rows. This is not an author or paper ratio. | Exact paper inputs remain 0/9. No Figure 13, Oracle, RTDL approximation-algorithm reproduction, author performance parity, or full-paper claim. |
| [RayDB paper](raydb-paper/README.md) | Generic signed-i64 partitioned ray/triangle grouped reductions, exact partition ledgers, prepared ray reuse, legacy ABI compatibility, and reconciled phase telemetry. | Complete grouped-row equality on all 13 deterministic same-source SSB queries at both SF10 (59,986,052 rows) and SF20 (119,994,608 rows) across DuckDB, the pinned author, and RTDL. | The aligned launch phase is unfavorable: author median `0.439941ms` vs RTDL `4.054084ms` at SF10, and `0.767822ms` vs `8.159624ms` at SF20; author wins 13/13 at both scales, with a disclosed topology mismatch. | Generated inputs are not verified paper bytes. Figure 12, modified Crystal, paper hardware/performance, author algorithm equivalence, whole-program speedup, zero-copy, and full-paper reproduction remain unclaimed. |
| Triangle Counting | Generic ray/triangle scalar summaries and segmented prepared execution. | Both application-owned RT-1A2 and RT-2A1 are exact against author triangle counts; DEFAULT selects between them zero times. | Current scoped cold and prepared measurements are preserved separately; no universal no-slower claim. | The application chooses the paper algorithm; V3 verifies its canonical physical family. |
| [Arkade](arkade-paper/README.md) | Generic prepared metric-kNN with L-infinity and normalized-cosine contracts, persistent GAS, radius doubling, and refit. | FR-L-infinity and MT-cosine are exact in V2 and V3 under the independent paper-metric oracle and behaviorally true-OptiX. | Cold and prepared measurements are both reported; prepared timing does not make preparation free. | The application chooses FR or MT; DEFAULT never chooses between them. |

These apps are not hidden benchmark rows. They are reader-facing reproduction
programs with explicit inputs, comparator boundaries, and output artifacts.
No current app claims complete reproduction of every original paper dataset,
figure, algorithmic implementation detail, and performance result.

The machine-readable current portfolio state is recorded in
[`paper_app_status_snapshot.json`](paper_app_status_snapshot.json).

## Adding A Paper App

New paper apps should start from [PAPER_APP_TEMPLATE.md](PAPER_APP_TEMPLATE.md)
and should include a `data/manifest.json` shaped by
[paper_app_manifest.schema.json](paper_app_manifest.schema.json).

The manifest is not a runtime input. It is a reader-facing contract that states:

- which RTDL public APIs the app exercises;
- which pieces remain app-owned;
- what reproduction scope is claimed;
- which comparator or expected output is used;
- which performance regime is being measured;
- which broader claims are not made.
