# Antigravity Completion Review for `goal4629`

## Verdict: `accept_goal4629_keep_candidate_not_promoted`

As the independent AI completion reviewer, Antigravity has reviewed the candidate decision packet for `goal4629`. We accept the decision to keep `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` as a Tier-2 candidate and not promote it to the measured catalog.

## Findings

1. **Validity of keeping candidate**: Correct. The evidence is derived from Goal4620's completion consensus, which explicitly accepted candidate completion but did not authorize measured-catalog promotion. Rerunning or promoting without a predeclared promotion gate would be an overclaim.
2. **Correct preservation of positive candidate value**: The document correctly highlights the positive outcomes of the candidate gate under "Why This Is Not A Rejection" (parity passes, device-output speedup, and avoiding host-side materialization) without treating it as a failure.
3. **Prevention of overclaiming**: All measured-catalog and release-surface claims are strictly marked as not authorized in the document, code, and tests.
4. **Triangle Counting Coverage**: Preserves Goal4627's classification of `triangle_counting` as `candidate_not_measured_release_coverage`.
5. **Robust Promotion Requirements**: The listed requirements (predeclaring the gate, expanding shape matrix, preserving correctness/metadata, and external promotion review) are appropriate and sufficient.
6. **Code-level Safeguards**: The Python module (`src/rtdsl/v4_weighted_sum_candidate_decision.py`) and associated tests (`tests/v4_goal4629_weighted_sum_candidate_decision_test.py`) enforce the decision programmatically, preventing any down-stream release scripts (like Goal4632) from miscounting the surface.
7. **Boundaries Preserved**: Non-authorization boundaries for V4 release, speedup claims, true-zero-copy, callbacks, C ABI, CuPy, and native kernels are completely preserved.

## Answers to Review Questions

**Q1: Is `keep_candidate_not_promoted` the right decision from the existing evidence?**
Yes. Goal4620's completion consensus explicitly accepted candidate completion and did not authorize measured-catalog promotion. The evidence covers only two ray/triangle shapes and candidate-gate repeats (5 repeats after 2 warmups). Promoting it without a predeclared promotion gate would be an overclaim.

**Q2: Does the document correctly preserve the positive candidate value without hiding it as a failure?**
Yes. The document includes a dedicated "Why This Is Not A Rejection" section, detailing correctness parity, device-output speedup, and the avoidance of host scalar reads/row materialization before the consumer.

**Q3: Does the document correctly prevent measured-catalog and release-surface overclaiming?**
Yes. The document explicitly declares measured-catalog promotion and release-surface use as "not authorized", and sets all associated claim-authorization flags to `False` in both code and tests.

**Q4: Does the decision preserve Goal4627's `triangle_counting` classification as candidate-bound?**
Yes. The document classifies `triangle_counting_release_coverage_after_goal4629` as `candidate_not_measured_release_coverage`, and the tests assert that the `triangle_counting` benchmark app status in `v4_coverage_audit` remains `candidate_not_measured_release_coverage`.

**Q5: Are the listed future promotion requirements sufficient for a later measured-catalog attempt?**
Yes. The five listed requirements (predeclaring the gate, expanding the same-contract shape matrix, preserving correctness parity, preserving device-output/no-hot-path metadata, and obtaining external review) cover process, coverage, correctness, and organizational checks.

**Q6: Are the tests and code-level scorecard adequate to prevent Goal4632 from miscounting this surface?**
Yes. The validation function `validate_v4_goal4629_weighted_sum_candidate_decision()` fails closed if any authorization flags are set to `True` or if the coverage status drifts. These checks are thoroughly covered by unit tests.

**Q7: Are all non-authorization boundaries preserved?**
Yes. The scorecard, code, and tests verify that V4 release, broad speedup claims, whole-app speedup claims, true-zero-copy wording, Tier-3 callback support, raw OptiX callback support, CuPy performance claims, C ABI embedding, and app-specific native kernels are not authorized.
