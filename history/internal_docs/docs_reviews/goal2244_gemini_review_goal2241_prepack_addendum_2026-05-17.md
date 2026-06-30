# Independent Gemini Addendum Review: Goal2241 Prepack Update

This is an independent Gemini addendum review, distinct from any Codex review.

## Review of Goal2241 Prepack Update

**Context:** This addendum review focuses on the post-review change to `scripts/goal2192_rayjoin_same_query_stream_runner.py` for Goal2241. Specifically, it examines the "prepack-once" optimization for PIP/OptiX backends, where PIP points and shapes are packed once per `run-stream` invocation and reused, and the `input_preparation_path` metadata is recorded.

## Questions and Answers:

### 1. Is the prepack-once change safe and limited to PIP/OptiX?

**Yes.** The prepack-once mechanism is strictly applied to the PIP/OptiX backend path. The `_prepare_backend_inputs` function in `scripts/goal2192_rayjoin_same_query_stream_runner.py` explicitly gates this optimization with `if workload == "pip" and backend == "optix"`. Furthermore, the `run_stream` function ensures that `_prepare_backend_inputs` is called only once per `run-stream` invocation to generate inputs, which are then reused across all warmups and repeats. The output metadata also accurately reflects this conditional preparation. This targeted application ensures safety and prevents unintended side effects on other workloads or backends.

### 2. Does it avoid changing the output contract or app/native boundary?

**Yes.** The change does not alter the output contract or app/native boundary. As confirmed in the previous review, the mapping from the generic `closed_shape_membership_2d_optix` primitive's output (`shape_id`, `membership`) to the RayJoin application-facing contract (`polygon_id`, `contains`) is deliberately handled in Python within the `_run_pip_optix_closed_shape` function. This Python-side translation ensures that the native engine remains app-agnostic, and the final results presented to the user or downstream systems adhere to the established RayJoin output contract.

### 3. Is it appropriate to measure the primitive with prepacked inputs, given the primitive accepts `PackedPoints` and `PackedPolygons`?

**Yes.** It is entirely appropriate to measure the primitive with prepacked inputs. As stated in `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md`, the underlying primitive (`closed_shape_membership_2d_optix`) accepts `PackedPoints` and `PackedPolygons`. Pre-packing these inputs once at the start of a `run-stream` invocation, and reusing them for all warmups and repeats, ensures that the timing measurements accurately reflect the performance of the primitive itself. This approach correctly isolates the primitive's execution time from the overhead of Python-level data packing, which would otherwise skew performance metrics.

### 4. Does the claim boundary remain narrow pending pod timing?

**Yes.** The claim boundary remains consistently narrow. The `claim_boundary` metadata within the runner's output payload explicitly disclaims "paper_scale_perf_claim_authorized" and "rtdl_beats_rayjoin_claim_authorized". Additionally, the report `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md` reiterates that this is an "implementation-path improvement, not a full RayJoin reproduction or broad paper-scale speedup claim." Both the code and documentation consistently maintain this narrow scope, indicating that no expanded claims will be made prior to full pod timing results.

## Verdict: `accept`
