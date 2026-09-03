# Goal5842 pre-GPU internal hostile self-review

Date: 2026-09-03

Verdict:
`READY_FOR_ONE_GENERATION_EXECUTION__NOT_GOAL5842_COMPLETE`.

This review authorizes no public performance wording. It records that the
committed experiment is ready to execute one create-only NVIDIA transaction.
Goal5842 still requires an exact replay on a second GPU architecture generation
and deferred external review before any broader conclusion.

## Scientific question and intervention

The primary question is whether the integrity work performed by RTDL's generic
family admission layer contributes measurable cold post-import latency. The
intervention is narrow:

- `CHECK_ON_COLD_PUBLIC_ADMISSION` calls the public `route.compile()` for the
  first time in a fresh process.
- `CHECK_OFF_COLD_UNCHECKED_CONSTRUCTION` calls the same route factory and the
  same provider projection, then constructs the same capability type through
  an experiment-private token while skipping generic admission integrity
  checks.
- No public admission runs before either registered interval. A normal public
  admission runs only afterward to establish exact plan, artifact, projection,
  and descriptor identities.
- The primary statistic uses only the provider-projection-and-admission phase.
  Full route-to-capability latency is secondary. The identical route phase is a
  negative control.

This intervention does not prove that checks can be removed safely. Target
materialization still revalidates plan, artifacts, descriptor, and projection.
The result can attribute only the measured generic-admission increment, not the
entire RTDL setup gap observed by earlier experiments.

## Defects found and repaired before freeze

1. The first draft admitted a reference program before timing, which warmed the
   admission path and invalidated a cold-start interpretation. That draft was
   discarded before any timing. Both arms are now cold.
2. The first draft mixed the identical route-construction phase into the
   primary statistic. The admission phase is now primary, route construction is
   a negative control, and their sum is secondary.
3. Phase labels incorrectly placed provider projection in route construction.
   Labels now match the actual call boundary: projection occurs in the second
   phase.
4. The baseline initially risked hiding target/toolchain construction and a
   second PyOptiX workload construction. Target/toolchain binding is now its own
   phase and PyOptiX consumes the already built frozen fixture.
5. Workloads were initially frozen only indirectly by source identities. The
   preregistration now fixes exact input, full-oracle, and public-output
   SHA-256 values, cardinalities, and three-arm eligibility for all three tasks.
6. Direct CUDA/OptiX exposes no destruction timing. Its close field is required
   to remain null and no cross-arm close ratio is permitted.

## Residual limitations

- Only relation and triangle have honest Direct CUDA/OptiX, current NVIDIA
  PyOptiX-compatible, and public checked RTDL arms. Sphere remains in the causal
  cohort but has no fabricated provider-performance comparator.
- The provider cohort establishes one exact semantic input/output contract per
  task. It does not claim byte-identical generated artifacts across three
  independently implemented systems.
- Direct and PyOptiX validate triangle per-ray output in addition to the common
  weighted scalar. Current public RTDL exposes the checked scalar; the stronger
  per-ray vector is not invented as an RTDL output.
- The unchecked arm is deliberately unsafe and experiment-only. Ratios against
  this potentially small denominator are forbidden.
- One Ada result cannot satisfy the preregistered two-generation gate. The final
  authority rejects duplicate architecture generations and duplicate GPU UUIDs
  and never computes cross-machine raw-time ratios.
- External AI review and consensus are unavailable while traveling and remain
  explicitly false.
- Several inherited Goal5796/5798 historical tests cannot execute in this
  checkout because old authority/result JSON files are absent. One old
  source-string assertion also predates later legitimate native capacity
  changes. Goal5842 therefore pins the current executable sources and supplies
  independent current contract, synthetic-transaction, runtime-oracle, and GPU
  evidence gates rather than claiming those historical suites pass.

## Verification before GPU execution

- Goal5842 focused tests: 21/21 passed.
- Goal5838 frozen-core and selected-route tests: 91/91 passed.
- Goal5840 refinement evidence tests: 65/65 passed.
- Goal5798 immutable input-reuse tests: 5/5 passed.
- Ruff format/check and Python bytecode compilation passed for all Goal5842
  Python entry points.
- The three Goal5838 frozen core files have no working-tree diff.
- Preregistration seal:
  `6f4cc3123e51d3a1d37193673fb943fca1610ab6536043c3cff774ed4d7f2536`.
- Preregistration state: 216 causal workers, 108 baseline composites, 216
  baseline subworkers, zero registered timings, zero GPU executions.

## Fail-closed execution rule

Before worker zero, environment repair is permitted. The execution authority
must bind a clean exact Git commit, Python environment, current native DSO and
build manifest, Direct binary, device source, CUDA/OptiX headers, PyOptiX/CuPy
identity, and physical GPU. The no-timing GPU witness must then prove on/off
executable and output identity for all three tasks.

After worker zero, no retry, row replacement, failed-row deletion, task or
phase change, or RTDL-only optimization is allowed. A failure is preserved as
the outcome of that transaction. A successful first-generation recount remains
`NOT_GOAL5842_COMPLETE` until the exact second-generation replay gate passes.
