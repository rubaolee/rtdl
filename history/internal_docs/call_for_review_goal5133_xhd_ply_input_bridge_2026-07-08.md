# Call For Review - Goal5133 X-HD PLY Input Bridge

Please strictly review Goal5133.

## Files To Review

```text
history/internal_docs/goal5133_xhd_ply_input_bridge_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny3d_ply_a.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny3d_ply_b.ply
Paper-reproduction-apps/x-hd-paper/results/tiny3d_ply_local_reference_summary.json
Paper-reproduction-apps/x-hd-paper/results/tiny3d_ply_rtdl_route_summary.json
tests/goal5133_xhd_ply_input_bridge_test.py
```

## Review Questions

1. Is the PLY bridge app-owned, not an RTDL core primitive?
2. Does the loader correctly support bounded ASCII PLY vertex rows while failing
   closed for unsupported binary PLY?
3. Do both gate runners correctly accept `--input-type wkt|ply`?
4. Does the author runner forward `--input-type ply` to `hd_exec -input_type ply`
   without claiming an author run occurred locally?
5. Does the RTDL route gate correctly read the tiny PLY fixture and match exact
   reference?
6. Was the misleading `load_wkt_sec` phase name removed for generic input loads?
7. Do the tests preserve existing WKT gates and add meaningful PLY coverage?
8. Does the report avoid claiming exact paper dataset reproduction,
   representative correctness, full-resolution Stanford success, or performance?
9. Is the next step correctly scoped as a bounded PLY gate on POD, not a
   full-resolution paper figure reproduction?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to 9 review questions:
1. ...
...
9. ...
```

## Requested Verdict Label

If acceptable:

```text
approve_goal5133_xhd_ply_input_bridge_ready_for_bounded_graphics_gate
```
