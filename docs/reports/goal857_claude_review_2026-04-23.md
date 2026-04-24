**Verdict: Approved — narrow, correct, well-bounded tooling change.**

Key reasons:

1. **Does exactly what it claims.** Both perf scripts now accept `--optix-mode {auto,host_indexed,native}`, propagate it through `run()`, and record it at both the top-level and per-case level in the JSON payload. Code matches the report description precisely.

2. **Non-applicable guard is correct.** When `backend != "optix"`, both scripts emit `"optix_mode": "not_applicable"` — the test `test_cli_writes_optix_mode_into_payload` verifies this with `cpu_python_reference`, preventing silent misleading labels.

3. **Tests cover the right surface.** Three tests: mode propagation through `goal726`, mode propagation through `goal729`, and CLI round-trip to disk. All use `mock.patch.object` scoped tightly to `module.app.run_case` — no leaking side effects.

4. **Boundary is clearly held.** The scripts' `boundary` strings and the report both explicitly state no RT-core claim is made. This is reinforced in code at `goal726:71` and `goal729:86`.

5. **No regressions introduced.** The only additions are a new parameter with a validated allowlist (`optix_mode in {"auto","host_indexed","native"}`) and output fields — no existing logic was restructured.

One minor note: the test for `goal729` passes `fake_run_case` returning a fixed dict that lacks `json.dumps`-sized counting (the real `_time_json_payload` calls `json.dumps` internally), but since the mock replaces `app.run_case` not `_time_json_payload`, the serialization path still runs. No issue.
