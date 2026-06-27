# Goal 1581: OptiX Collect-K Candidate Preset Broader Pod Validation

## Verdict

`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` passed a broader committed-state pod validation on `NVIDIA RTX 4000 Ada Generation` at commit `63272caeb52ce0210b990878486bbaad824a55db`. This is useful validation evidence, but it is not promotion clearance because the targeted rerun still shows a noisy/negative 49153-count alias case.

## Run Scope

- Pod checkout: `/root/rtdl_goal1545_pod`
- Commit: `63272caeb52ce0210b990878486bbaad824a55db`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- CUDA runtime path: `/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- OptiX library: `build/librtdl_optix.so`
- Command: `PYTHONPATH=src:. python3 scripts/goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py --library build/librtdl_optix.so --output-prefix /tmp/goal1581_candidate_full --repeats 5 --targeted-repeats 9 --candidate-preset-smoke --ld-library-path /usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`

## Acceptance

- Focused static tests: `Ran 17 tests`, `OK`.
- Baseline accepted: `True`.
- Alias accepted: `True`.
- Baseline parity: `True`.
- Alias parity: `True`.
- Baseline topology: `True`.
- Alias topology: `True`.
- Candidate preset accepted: `True`.
- Candidate preset parity: `True`.
- Candidate preset topology: `True`.

## Sweep Results

| Count | Baseline ms | Alias ms | Delta ms | Baseline payload copies | Alias payload copies | Parity |
|---:|---:|---:|---:|---:|---:|---|
| 7 | 0.048041 | 0.044955 | -0.003086 | 0 | 0 | True |
| 8192 | 0.107734 | 0.107824 | 0.000090 | 0 | 0 | True |
| 12289 | 0.138742 | 0.135035 | -0.003707 | 1 | 1 | True |
| 16385 | 0.172847 | 0.163360 | -0.009487 | 3 | 0 | True |
| 20481 | 0.167357 | 0.165433 | -0.001924 | 2 | 1 | True |
| 24577 | 0.168328 | 0.167918 | -0.000410 | 2 | 1 | True |
| 32769 | 0.214596 | 0.199979 | -0.014617 | 4 | 0 | True |
| 45057 | 0.208875 | 0.203035 | -0.005840 | 2 | 1 | True |
| 49153 | 0.219365 | 0.209507 | -0.009858 | 3 | 1 | True |
| 65536 | 0.210889 | 0.209787 | -0.001102 | 0 | 0 | True |
| 65537 | 0.315077 | 0.264832 | -0.050245 | 5 | 0 | True |

## Targeted Rerun

| Count | Targeted baseline ms | Targeted alias ms | Delta ms | Baseline payload copies | Alias payload copies | Parity |
|---:|---:|---:|---:|---:|---:|---|
| 49153 | 0.220638 | 0.273678 | 0.053040 | 3 | 1 | True |
| 65536 | 0.212413 | 0.214897 | 0.002484 | 0 | 0 | True |
| 65537 | 0.283106 | 0.265132 | -0.017974 | 5 | 0 | True |

## Candidate Preset Smoke

| Count | Candidate preset ms | Payload copies | Parity |
|---:|---:|---:|---|
| 49153 | 0.216660 | 1 | True |
| 65536 | 0.213365 | 0 | True |
| 65537 | 0.268278 | 0 | True |

## Interpretation

The single-flag preset maps to an accepted parity/topology-preserving candidate path. It successfully exercises the same derived carry alias behavior without enabling rejected pointer-carry diagnostics.

The performance picture remains promising but not final. The 5-repeat sweep improved most counts, including the highest odd carry case `65537`, but the 9-repeat targeted rerun showed `49153` alias slower than baseline in that session. Treat this as a remaining measurement-stability/promotion blocker, not a correctness blocker.

## Claim Boundary

This report does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
