I have now reviewed all specified files. Here is the complete assessment.

---

## RTDL v2.3 App-Portfolio Release Review

### Criteria Check

**VERSION / front-door docs identity**
- `VERSION` = `v2.3` ✓
- `README.md`, `docs/README.md`, `docs/current_architecture.md` all contain `"current released version is \`v2.3\`"`, `"source-tree"`, and `"Python+partner+RTDL"` ✓

**Two app summary tables — separation correctness**

Both primary tables (in `docs/application_catalog.md` and `docs/release_reports/v2_3/README.md`) are present and correctly separated:
- `### Promoted Benchmark Apps` / `## Promoted Benchmark Apps` — all nine apps present (Hausdorff, Spatial RayJoin, RT-DBSCAN, Robot collision, RayDB, Barnes-Hut, LibRTS, RTNN, Triangle counting) ✓
- `### Learner And Example Apps` / `## Learner And Example Apps` — all expected groups present (getting started, feature families, partner examples, geospatial, ML, analytics, robotics, simulation, trajectory, GPU-RMQ research, visual demos) ✓
- The separation is clean: no promoted-benchmark entry appears in the learner table and vice versa ✓

**GPU-RMQ demotion**
- Catalog `### Promoted Benchmark Apps` — GPU-RMQ is absent ✓
- Catalog `### Learner And Example Apps` row: `"Explicitly demoted research/learner app after Goal2612"` ✓
- Catalog analytical table row: `"Goal2612 rejects benchmark promotion for the current design: RTDL remains much slower than direct CUDA sparse-query code"` ✓
- `docs/release_reports/v2_3/README.md` "What v2.3 Does Not Claim": `"No GPU-RMQ benchmark promotion is claimed; Goal2612 demotes it."` ✓
- `examples/README.md` "Important Performance Applications": `"Demoted research/learner app after Goal2612"` ✓
- `examples/v2_0/research_benchmarks/README.md`: `"Goal2612 shows the current RTDL design is not benchmark-competitive against direct CUDA sparse-query code"` ✓
- Goal2612 demotion doc is thorough: 13.8x–23.5x slower on query time; decision is explicit and documents follow-up boundary; native engine is kept generic (`"boundary that native engines must not learn RMQ-specific formulas"`) ✓

**Continuous Frechet demotion**
- Catalog learner table: `"Explicitly demoted learner/demo app"` ✓
- Release report learner table: `"Demoted learner/demo app"` ✓
- Release report "What v2.3 Does Not Claim": `"No Continuous Frechet benchmark promotion is claimed; Goal2583/2584 demote it."` ✓
- Continuous Frechet is correctly absent from the promoted-benchmark table in both canonical docs ✓

**Release boundary — no overclaims**

| Claim | Status |
|---|---|
| Package install / pip / PyPI | Explicitly disclaimed: `"not a package-install release"`, `"No package metadata, PyPI artifact, or install command is published"` ✓ |
| Broad RT-core / universal speedup | `"not a broad RT-core speedup claim"`, `"No universal speedup claim is made for backend flags such as \`--backend optix\`"` ✓ |
| Whole-application speedup | `"not a whole-application speedup claim"`, `"No whole-application speedup claim is made for the benchmark portfolio"` ✓ |
| Paper reproduction | `"No paper-reproduction claim is made unless a specific report says so for a specific subpath"` ✓ |
| Arbitrary PyTorch/CuPy acceleration | `"not a claim that RTDL optimizes arbitrary PyTorch or CuPy programs"`, `"No arbitrary PyTorch/CuPy acceleration claim is made"` ✓ |
| App-specific native engine semantics | GPU-RMQ-derived primitive extracted as generic `grouped_candidate_argmin`; `"without adding RMQ-specific native-engine logic"` ✓ |

**Test gate (`goal2613_v2_3_app_portfolio_release_test.py`) — static analysis**

All four test methods pass on the current document state:
- `test_version_and_front_door_docs_name_v2_3` — all three doc substring checks pass ✓
- `test_release_package_has_two_app_tables` — all 9 promoted + 13 learner names found ✓
- `test_catalog_demotes_gpu_rmq_and_continuous_frechet` — all four assertions pass; banned phrase absent ✓
- `test_release_blocks_overclaims` — all five forbidden-overclaim phrases present in release report ✓

**Coherence as a source-tree app-portfolio release**
- All example commands use `PYTHONPATH=src:.` throughout ✓
- Benchmark apps are framed as "reconstruction instruments", not speedup proofs ✓
- `examples/v2_0/research_benchmarks/README.md` correctly lists all 10 studies (9 promoted + 1 demoted) ✓

### Minor Observations (non-blocking)

1. **`examples/README.md` "Important Performance Applications" table** lists only 5 of 9 promoted benchmarks (omits RT-DBSCAN, Robot collision, RayDB, Barnes-Hut, LibRTS). The definitive catalog and release report tables are complete and correct; this is a navigation convenience table, not a gate. Not a blocker.

2. **Evidence section in `docs/release_reports/v2_3/README.md`** links to Goal2612 (GPU-RMQ demotion) but has no hyperlink to Goal2583/2584 (Continuous Frechet demotion), even though those reports are referenced by name in the "What v2.3 Does Not Claim" section. The reports exist in the working directory. Not a blocker.

---

**VERDICT: ACCEPT**

All blocking criteria are satisfied. The two app summary tables correctly separate promoted benchmark apps from learner/example apps in both canonical docs. GPU-RMQ and Continuous Frechet are explicitly demoted with documented evidence. The release boundary contains no package-install, broad-speedup, whole-app-speedup, paper-reproduction, arbitrary-PyTorch/CuPy, or app-specific native-engine claims. The test gate passes on the current document state. v2.3 is coherent as a source-tree app-portfolio release.
