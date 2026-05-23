# Goal2480 Consensus: Robot Collision CPU Reference App

Date: 2026-05-21

## Consensus: Approved

Codex, Gemini, and Claude agree that Goal2480 can close and that work can move
to Goal2481 generic RTDL contract design.

## Reviewed Artifacts

- `docs/reports/goal2479_robot_collision_benchmark_roadmap_2026-05-21.md`
- `docs/reports/goal2480_robot_collision_cpu_reference_app_2026-05-21.md`
- `examples/v2_0/research_benchmarks/robot_collision/README.md`
- `examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`
- `tests/goal2480_robot_collision_cpu_reference_app_test.py`
- `examples/v2_0/research_benchmarks/README.md`

## External Review Verdicts

Gemini:

- Verdict: Approved.
- Blocking issues: none.
- Non-blocking follow-ups: Goal2481 should explicitly decide whether the native
  contract remains 2D or generalizes to 3D; paper citation/DOI/venue/code/data
  must remain blocked before public wording.

Claude:

- Verdict: Approved.
- Blocking issues: none.
- Non-blocking follow-ups: accept Gemini's 2D/3D and citation recheck items,
  tighten the continuous-collision claim-boundary assertion, and broaden native
  vocabulary scans during Goal2481.

## Accepted Follow-Ups

- Goal2480 now documents that the CPU reference is intentionally 2D and that
  Goal2481 must decide the 2D-vs-3D native contract before Embree/OptiX work.
- Goal2480 tests now assert `continuous_collision_supported = false`.
- Goal2480 keeps paper reproduction, authors-code comparison, public speedup,
  continuous collision, and native implementation claims blocked.
- Goal2481 must broaden native vocabulary enforcement beyond ABI-prefix scans.

## Closure Decision

Goal2480 satisfies the roadmap exit criteria:

- deterministic CPU reference app exists;
- tiny fixture has exact expected compact any-hit labels;
- scaled fixture exercises configurable batching;
- JSON metadata exposes the output contract and claim boundaries;
- no native code was touched;
- no robot-specific native ABI was added.

Next gate: Goal2481 generic contract design. No native Embree or OptiX work
should begin until Goal2481 is reviewed.
