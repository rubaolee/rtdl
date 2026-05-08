# Goal 1586: OptiX Collect-K Multi-Session Runner

## Verdict

Added a reusable multi-session validation runner for the OptiX `COLLECT_K_BOUNDED` candidate preset. The runner prevents manual output-prefix mistakes by creating explicit per-session prefixes and aggregating the targeted baseline, alias, and candidate-preset results into compact JSON and Markdown summaries.

## Files

- Runner: `scripts/goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py`
- Static test: `tests/goal1586_v1_5_4_optix_collect_k_multi_session_runner_test.py`

## Local Validation

- Command: `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1586_v1_5_4_optix_collect_k_multi_session_runner_test tests.goal1579_v1_5_4_optix_collect_k_next_arch_runner_test`
- Result: `Ran 6 tests`, `OK`.

## Pod Smoke

- Pod checkout: `/root/rtdl_goal1545_pod`
- Commit: `7cb19d78`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Static test: `PYTHONPATH=src:. python3 -m unittest tests.goal1586_v1_5_4_optix_collect_k_multi_session_runner_test`
- Static result: `Ran 3 tests`, `OK`.
- Smoke command: `PYTHONPATH=src:. python3 scripts/goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py --sessions 1 --library build/librtdl_optix.so --output-prefix /tmp/goal1586_smoke --repeats 1 --targeted-repeats 1 --candidate-preset-repeats 1 --ld-library-path /usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Smoke result: `goal1586_multi_session_validation_recorded`.
- Summary JSON: `/tmp/goal1586_smoke_summary.json`
- Summary Markdown: `/tmp/goal1586_smoke_summary.md`

## Use

For a full three-session pod validation:

```bash
LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64 \
PYTHONPATH=src:. \
python3 scripts/goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py \
  --sessions 3 \
  --library build/librtdl_optix.so \
  --output-prefix /tmp/goal1586_multi_session \
  --repeats 5 \
  --targeted-repeats 9 \
  --candidate-preset-repeats 5 \
  --ld-library-path /usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64
```

## Claim Boundary

This runner records repeated validation sessions only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
