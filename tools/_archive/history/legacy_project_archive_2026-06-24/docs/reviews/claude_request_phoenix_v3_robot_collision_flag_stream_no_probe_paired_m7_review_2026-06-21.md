# Claude Review Request - Phoenix V3 Robot Collision Flag-Stream No-Probe Paired M7 Review

Please critically review the Phoenix V3 robot collision flag-stream no-probe
paired RTX evidence packet:

`docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md`

and:

`docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.json`

Also inspect the copied pod artifact:

`docs/rebuild/v3/evidence/phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621/summary.json`

Context:

The prior robot-collision boundary was not M7 because the hot prepared flag
stream was fast, but full wall timing was dominated by the CPU probe-reference
oracle:

- hot tail OptiX speedup vs Embree: about 5.166x;
- traversal OptiX speedup vs Embree: about 69.904x;
- validation-inclusive wall OptiX/Embree: about 0.997x;
- CPU probe-reference: about 187 seconds per backend in the old artifact.

The new packet separates validation from performance timing:

- validation rows keep CPU probe-reference enabled and pass for both backends;
- timed rows use `--no-probe-reference`;
- timed rows preserve the same prepared grouped segment any-hit flag-stream
  contract and shape;
- five no-probe paired process samples all have wrapper speedup above 1x;
- no release/public wording is authorized before review.

Candidate wording under review:

```text
RTDL V3 includes a generic collision_flag_stream route where, on the 8,192-pose
/ 147,456-segment discrete sampled probe contract on a single RTX 4000 Ada pod,
prepared OptiX grouped segment any-hit flags beat the same-contract Embree route
across five no-probe paired process samples: tail prepared invocation speedup
mean 5.086x, total-run window speedup mean 5.075x, and no-probe wrapper speedup
mean 1.171x with weakest no-probe wrapper speedup 1.083x. CPU probe-reference
validation was run separately and matched both backends. This is sampled
flag-stream evidence, not full robot planning, exact solid collision, or
continuous collision.
```

Please return Markdown only and do not edit files.

Required verdict shape:

1. Verdict: approve, approve with amendments, or reject.
2. Whether separating CPU probe-reference validation from no-probe performance
   timing is acceptable for row-scoped M7, given the wording.
3. Whether the wrapper/tail/window timing definitions are clear enough.
4. Whether this is genuinely a V3 generic engine capability row rather than
   app-specific native-engine work.
5. Any remaining P0/P1 fixes.
6. Exact final allowed wording if approved.
7. Exact forbidden wording.

Guardrails:

- Do not approve broad V3-over-V2 claims.
- Do not approve full robot-planning claims.
- Do not approve exact solid collision or continuous collision claims.
- Do not approve zero-copy claims.
- Do not approve whole-app end-to-end claims that include the CPU oracle.
- Keep any approval row-scoped, same-contract, same-shape, and single-pod.
