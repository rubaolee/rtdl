# Goal864 External Review — Claude

Date: 2026-04-23
Reviewer: Claude (Sonnet 4.6)
Verdict: **ACCEPT**

## Question 1: Does `needs_real_optix_artifact` correctly describe the local state?

Yes. `_recommended_status()` enters the `needs_real_optix_artifact` branch whenever
`_all_required_ok()` is False. That helper requires all three labels
(`cpu_python_reference`, `optix_host_indexed`, `optix_native`) to carry status `"ok"`.
In the local artifact, `cpu_python_reference` is `ok` and both OptiX records are
`unavailable_or_failed` (FileNotFoundError: librtdl_optix not found). The label
correctly names the gap: a real OptiX build is needed before promotion can be
evaluated. No mislabelling.

Minor note: if `cpu_python_reference` itself failed, the function would still return
`needs_real_optix_artifact`, which is a slightly misleading label for that edge case.
This is not load-bearing for the current use — CPU reference is a pure Python path
that cannot fail due to a missing OptiX library — and is not worth blocking on.

## Question 2: Does the packet avoid overpromoting segment/polygon?

Yes. Multiple independent brakes are in place:

- `recommended_status: needs_real_optix_artifact` (hard block, shown in both JSON and Markdown)
- `strict_pass: false`
- `required_records_ok: false`, `required_parity_ok: false`
- Explicit `boundary` field: "does not promote segment/polygon to an active RTX claim path
  and does not authorize a public speedup claim"
- The Goal807 source artifact carries a matching `boundary` and `activation_rule`

No path through the current logic allows `ready_for_review` without both OptiX records
being `ok` and parity-matched against CPU reference. The packet is conservative.

## Question 3: Is there a logic hole in the recommendation mapping?

No significant holes. Trace:

1. Any required record not `ok` → `needs_real_optix_artifact` (catches missing library, crash, missing label)
2. Any required record lacking parity → `blocked_by_gate_failure`
3. `include_postgis=True` and PostGIS not ok or no parity → `blocked_by_gate_failure`
4. All checks pass → `ready_for_review`

The mapping is exhaustive for the defined record set. One minor structural oddity:
the `source_path` field in `build_packet()` uses a full payload equality comparison to
detect the default input path; `main()` overrides it unconditionally anyway, so it has
no effect on outputs. This is not a logic hole in the recommendation path.

## Conclusion

The packet is honest about what the local Mac run can and cannot prove. It does not
inflate the segment/polygon family's promotion status. The recommendation logic is
sound. Tests cover the key branches (all-missing, partial, full-pass, CLI).

**ACCEPT**
