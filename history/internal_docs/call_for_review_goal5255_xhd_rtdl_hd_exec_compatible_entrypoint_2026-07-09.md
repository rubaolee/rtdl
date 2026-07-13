# Call For Review - Goal5255 X-HD RTDL hd_exec-Compatible Entrypoint

Please strictly review Goal5255.

## Files Under Review

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
Paper-reproduction-apps/x-hd-paper/README.md
```

## Context

The X-HD line has many correctness/performance gates, but the user-facing app
shape was still gate-centric. Goal5255 adds an app-owned RTDL runner that accepts
the author's key `hd_exec` flags and writes author-shaped `HDResult` / `Running`
JSON.

This is meant to improve the paper app user experience, not to make a new
performance claim.

## Questions

1. Does `run_xhd_rtdl_hd_exec.py` genuinely expose the author's key CLI flag
   shape (`-input1`, `-input2`, `-n_dims`, `-input_type`, `-variant`,
   `-execution`, `-json`) while keeping RTDL-specific route selection clearly
   labeled as an extension?

2. Is `HDResult` correctly defined as directed `input1 -> input2`, matching the
   Goal5126 directed-asymmetric finding, rather than silently returning a
   symmetric Hausdorff max?

3. Are route labels strong enough? In particular, does the output make it hard
   to confuse:

```text
public-columnar
cell-mbr-fast-scalar
cell-mbr-exact-witness
```

4. Does the runner fail closed for unsupported author variants and unsupported
   `input_type=image` instead of pretending coverage it does not have?

5. Does the new JSON output preserve enough author compatibility (`HDResult`,
   `Running.AvgTime`, `Running.Repeats`) without hiding the fact that this is an
   RTDL route under the `RTDL` metadata block?

6. Does the implementation remain app-owned, without adding X-HD, hd_exec,
   paper, ModelNet40, or file-format semantics to RTDL core?

7. Do the tests protect the most important semantic hazard: the directed
   asymmetric fixture must produce `HDResult=0.5`, not the symmetric value 9.0?

8. Does the README wording describe the entrypoint accurately without implying
   full paper reproduction, exact dataset identity, author RT-core equivalence,
   or performance parity?

9. Are there any hidden performance claims caused by writing `Running.AvgTime`
   in author-shaped JSON? Should any wording be tightened to say this is RTDL
   route wall time, not author internal `Running.AvgTime`?

10. Should Goal5255 be accepted as an app-usability/contract milestone before
    further X-HD algorithm/performance work?

## Expected Answer Shape

Please answer in this format:

```text
Verdict: approve | approve_with_required_amendments | revise | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
10. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goal5255_xhd_rtdl_hd_exec_compatible_entrypoint
```
