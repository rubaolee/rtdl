# Call For Review - Goal5266 X-HD hd_exec Graphics ThaiStatuette -> AsianDragon Entrypoint

Date: 2026-07-09

## Review Request

Please strictly review Goal5266, which extends the X-HD RTDL
`hd_exec`-compatible entrypoint evidence to:

```text
ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3
```

## Files To Review

```text
history/internal_docs/goal5266_xhd_hd_exec_graphics_thai_asian_entrypoint_result_2026-07-09.md
tests/goal5266_xhd_hd_exec_graphics_thai_asian_pod_artifact_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Questions

1. Does the author hd_exec rerun on ThaiStatuette scaled 1e-3 -> AsianDragon
   scaled 1e-3 match the paper-branch log HDResult within the established
   1e-6 bounded tolerance?
2. Does the RTDL `cell-mbr-exact-witness` route match the author rerun within
   the established 1e-6 bounded tolerance?
3. Does the RTDL artifact preserve `per_source_witness_exact=true` and avoid
   the earlier fast-scalar approximate-witness caveat?
4. Are point counts and preprocessing correctly recorded
   (`4999996/3609600`, `translate_each_input_to_min_bound`)?
5. Does the documentation keep the result at Level-B same-source/scaled
   candidate status rather than exact paper byte-input identity?
6. Does the packet avoid author performance parity, speedup, full-paper, and
   author RT-core equivalence claims?
7. Is it correct to treat this as another graphics representative entrypoint
   gate, not as a complete Figure 5 or Figure 5-11 reproduction?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-7:
```
