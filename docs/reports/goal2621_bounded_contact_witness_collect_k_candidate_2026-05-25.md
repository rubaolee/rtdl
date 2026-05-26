# Goal2621 Bounded Contact-Witness COLLECT_K_BOUNDED Benchmark Promotion

Date: 2026-05-25

Status: contract and Python+RTDL candidate implemented with local Embree parity
and RTX A5000 OptiX parity evidence. Follow-up 3-AI review promoted the app to
an internal benchmark app and promoted `COLLECT_K_BOUNDED` to stable primitive
status. This report does not authorize public speedup claims.

## Goal

Promote a bounded collision witness/contact-manifold app toward benchmark
status while using it to stabilize `COLLECT_K_BOUNDED` as a generic primitive.
The app may use contact/collision vocabulary, but the engine primitive must only
own bounded witness-row collection.

## Implemented Surface

- New app directory:
  `examples/v2_0/research_benchmarks/contact_manifold/`.
- Main runnable:
  `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`.
- Contract rows:
  `(query_group_id, query_triangle_id, scene_triangle_id)`.
- Python oracle:
  deterministic exact 2-D triangle-intersection rows.
- Generic RTDL path:
  `rtdsl.collect_k_bounded_rows(..., row_width=3)` plus
  `rtdsl.validate_collect_k_bounded_result(...)`.
- Overflow behavior:
  exact fail-closed exception before returning partial rows.
- App-owned contact summaries:
  representative midpoint metadata derived after row collection; not a native
  engine primitive.

## Local Evidence

Commands run from repo root:

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test.py
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode scope
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode collect_k_reference --dataset tiny --witness-capacity 3
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode native_collect_k --backend embree --dataset tiny --witness-capacity 3
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode cpp_baseline --dataset tiny --repeat-count 5
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode cpp_baseline --dataset grid --grid-count 512 --repeat-count 5
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode baseline_comparison --dataset grid --grid-count 512 --witness-capacity 512 --repeat-count 3
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode baseline_comparison --dataset grid --grid-count 128 --witness-capacity 128 --repeat-count 3
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode collect_k_reference --dataset tiny --witness-capacity 2
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode native_collect_k --backend embree --dataset tiny --witness-capacity 2
```

Observed:

- Unit tests: 8 tests passed.
- Tiny deterministic fixture rows:
  `((0, 10, 0), (0, 11, 1), (2, 30, 2))`.
- Generic collect path matched CPU oracle with `witness_capacity=3`.
- Local Embree generic native collector path used
  `/Users/rl2025/rtdl_python_only/build/librtdl_embree.dylib` and exported
  `rtdl_embree_collect_k_bounded_i64`; rows matched CPU oracle.
- Standalone non-RTDL C++ exact baseline was added at
  `examples/v2_0/research_benchmarks/contact_manifold/cpp_contact_witness_baseline.cpp`.
- C++ tiny baseline matched the same three rows; best time over 5 repeats was
  about `6.66e-07` seconds on this Mac.
- C++ grid-512 baseline matched 512 rows; best time over 5 repeats was about
  `0.0158405` seconds.
- Python exact baseline on grid-512 matched 512 rows; best time over 3 repeats
  was about `4.30796462498256` seconds. The generic collect step over already
  materialized rows took about `0.0007194170029833913` seconds, which is only
  collection overhead and not a collision-detection baseline.
- Overflow with `witness_capacity=2` exited nonzero and raised:
  `COLLECT_K_BOUNDED overflowed capacity 2; emitted 3; failure_mode=fail_closed_overflow; partial_result_returned=False`.
- Local Embree generic native collector overflow also exited nonzero with the
  same fail-closed error.
- Grid smoke with 128 rows matched CPU reference.

## Engine Boundary

Accepted:

- `COLLECT_K_BOUNDED` owns canonical bounded `int64` row materialization.
- The app owns triangle-intersection fixture generation, contact terminology,
  and contact-summary interpretation.
- Future Embree/OptiX checks must emit the same generic row schema and pass the
  same fail-closed overflow contract.

Rejected:

- No collision-specific native primitive.
- No contact-manifold native ABI.
- No physics-library semantics inside RTDL engine.
- No partial row return or silent truncation on overflow.

## Documentation Updates

- Added the candidate to
  `examples/v2_0/research_benchmarks/README.md`.
- Added a candidate benchmark section to `docs/application_catalog.md`.
- Updated `docs/rtdl_primitive_catalog.md` with the bounded witness-row pressure
  and benchmark-app primitive-injection history.
- Added the candidate CLI to `scripts/goal2617_surface_smoke.py`.

## Pod OptiX Evidence

Evidence file:
`docs/reports/goal2621_contact_manifold_optix_pod_evidence_2026-05-25.md`.

Pod command requested by the user:

```bash
ssh root@69.30.85.198 -p 22148 -i ~/.ssh/id_ed25519
```

The Mac did not have `~/.ssh/id_ed25519`; the working RTDL key used was
`~/.ssh/id_ed25519_rtdl_codex`.

Observed on the pod:

- GPU: NVIDIA RTX A5000, driver 570.211.01, 24564 MiB.
- OptiX headers: `/root/vendor/optix-dev-9.0.0/include/optix.h`.
- CUDA prefix: `/usr/local/cuda-12.8`.
- OptiX build passed with
  `make build-optix OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 CUDA_PREFIX=/usr/local/cuda-12.8`.
- Tiny OptiX generic collector parity passed:
  `valid_count=3`, `matches_cpu_reference=True`.
- Grid-512 OptiX generic collector parity passed:
  `valid_count=512`, `matches_cpu_reference=True`,
  `native_collect_elapsed_sec=0.00221424363553524`.
- Tiny capacity-2 overflow failed closed with
  `failure_mode=fail_closed_overflow; partial_result_returned=False`.
- The candidate unit test passed on the pod:
  `Ran 8 tests ... OK (skipped=1)`.

## Promotion Closure And Qualifications

- Embree parity for the generic native collector was locally validated on this
  Mac. Linux Embree parity has not been separately recorded; this is a
  qualification, not a blocker, because RTX A5000 OptiX parity is recorded on
  Linux and Embree parity is recorded locally.
- OptiX parity on an NVIDIA pod for the same row schema and overflow contract
  is recorded.
- Standalone C++ CPU baseline exists; CUDA/BVH or physics-library baseline is
  optional future evidence, not a promotion blocker.
- Follow-up 3-AI consensus accepted promoted internal benchmark wording and
  stable `COLLECT_K_BOUNDED` wording.

## External Review State

- Claude review:
  `docs/reports/goal2621_claude_bounded_contact_witness_review_2026-05-25.md`.
- Gemini review:
  `docs/reports/goal2621_gemini_bounded_contact_witness_review_2026-05-25.md`.
- Initial reviews accepted the app as a benchmark candidate, not a promoted
  benchmark, pending backend/baseline evidence.
- Follow-up Claude review:
  `docs/reports/goal2621_claude_followup_promotion_review_2026-05-25.md`.
- Follow-up Gemini review:
  `docs/reports/goal2621_gemini_followup_promotion_review_2026-05-25.md`.
- Follow-up consensus is appended to
  `docs/reports/goal2621_bounded_contact_witness_collect_k_3ai_consensus_2026-05-25.md`.
- Claude flagged that the `overflow` dataset alias was potentially surprising;
  the app and README now state that overflow is controlled by capacity over the
  tiny scene, not by a separate scene.

## Current Conclusion

The app contract is ready and correctly exercises `COLLECT_K_BOUNDED` without
app-specific engine logic. Local Embree parity, pod OptiX parity, standalone
C++ baseline evidence, and follow-up 3-AI promotion consensus are recorded.
Goal2621 is promoted as an internal benchmark app, and `COLLECT_K_BOUNDED` is
promoted as a stable primitive. No public speedup claim is authorized.
